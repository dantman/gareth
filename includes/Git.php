<?php

abstract class ShellHandler {

	protected $stdin = null;
	protected $stdout = null;

	public function handle( $h, $pipes ) {
		$this->h = $h;
		$this->pipes = $pipes;

		stream_set_blocking( $pipes[1], false );
		stream_set_blocking( $pipes[2], false );

		$result = $this->run();
		return $result;
	}

	public function loop() {
		$inputChunk = false;

	 	$err_open = !feof($this->pipes[2]);
	 	$inp_open = !feof($this->pipes[0]);
		$out_open = !feof($this->pipes[1]);
		while( $err_open || $out_open ) {
			$read = array();
			$write = null;
			if ( $err_open ) {
				$read[] = $this->pipes[2];
			}
			if ( $inp_open ) {
				$write = array( $this->pipes[0] );
			}
			if ( $out_open ) {
				$read[] = $this->pipes[1];
			}
			$except = null;
			if ( false === stream_select( $read, $write, $except, 15 ) ) {
				throw new Exception( 'stream_select failed' );
			}

			if ( in_array( $this->pipes[2], $read ) ) {
				$chunk = fread( $this->pipes[2], 8192 );
				if ( $chunk === false ) {
					$out_open = false;
				}
				if ( $chunk ) {
					trigger_error( "git stderr: $chunk", E_USER_WARNING );
				}
			}
			if ( $write && in_array( $this->pipes[0], $write ) ) {
				if ( !$inputChunk && $this->stdin ) {
					$inputChunk = call_user_func( $this->stdin );
				}
				if ( $inputChunk ) {
					$len = fwrite( $this->pipes[0], $inputChunk );
					if ( $len === false ) {
						throw new Exception( "Error while trying to write to git's stdin." );
					}
					$inputChunk = substr( $inputChunk, $len );
				} else {
					// Don't need to write to stdin anymore
					fclose( $this->pipes[0] );
					$inp_open = false;
				}
			}
			if ( in_array( $this->pipes[1], $read ) ) {
				$chunk = fread( $this->pipes[1], 8192 );
				if ( $chunk === false ) {
					$err_open = false;
				}
				if ( $this->stdout ) {
					call_user_func( $this->stdout, $chunk );
				}
			}
			if ( feof( $this->pipes[2] ) ) {
				$err_open = false;
			}
			if ( feof( $this->pipes[1] ) ) {
				$out_open = false;
			}
		}

		fclose( $this->pipes[2] );
		fclose( $this->pipes[1] );
	}

	public function exitCode() {
		$this->loop();
		return proc_close( $this->h );
	}

}

class ShellExitBooleanHandler extends ShellHandler {

	public function run() {
		// This handler returns a boolean.
		// If the program exits with an exit code of 0 it returns true
		// otherwise it returns false indicating failure.
		return $this->exitCode() == 0;
	}

}

class ShellStdexchangeHandler extends ShellHandler {

	public function __construct( $input, $trim = false ) {
		$this->input = $input;
		$this->trim = $trim;
	}

	public function run() {
		$out = '';
		$input = $this->input;
		$this->stdin = function() use( &$input ) {
			$in = $input;
			$input = false;
			return $in;
		};
		$this->stdout = function( $chunk ) use( &$out ) {
			$out .= $chunk;
		};
		if ( $this->exitCode() != 0 ) {
			return false;
		}
		if ( $this->trim ) {
			$out = rtrim( $out );
		}
		return $out;
	}

}

class ShellGitTreeEntry {

	protected $attributes, $object, $name;

	public function __construct() {
		$this->attributes = octdec( '100644' );
		$this->object = false;
		$this->name = false;
	}

	public function setAttributes( $attributes ) {
		if ( is_string( $attributes ) ) {
			$attributes = octdec( $attributes );
		}
		$this->attributes = $attributes;
	}

	public function setObject( $object ) {
		$this->object = $object;
	}

	public function setName( $name ) {
		$this->name = $name;
	}

	public function getAttributes() {
		return $this->attributes;
	}

	public function getObject() {
		return $this->object;
	}

	public function getName() {
		return $this->name;
	}

	public function isValid() {
		return $this->object && $this->object->getOid() && $this->name;
	}

}

class ShellGitTree implements IteratorAggregate {

	protected $git, $odb;
	protected $oid;

	public function __construct( $git, $odb ) {
		$this->git = $git;
		$this->odb = $odb;
		$this->tree = array();
		$this->oid = false;
	}

	public function getIterator() {
		return new ArrayIterator( $this->tree );
	}

	public static function parse( $git, $odb, $str, $oid = false ) {
		if ( !$odb ) {
			return false;
		}
		$tree = new self( $git, $odb );
		$lines = explode( "\n", rtrim( $str ) );
		foreach ( $lines as $line ) {
			if ( preg_match( '/^(\d+) (\S+) (\S+)	(\S+)$/', $line, $m ) ) {
				$entry = $tree->insert();
				$entry->setAttributes( $m[1] );
				$entry->setName( $m[4] );
				$entry->setObject( $odb->read( $m[3] ) ); // @fixme Defer read until requested
			} else {
				throw new Exception( "Invalid ls-tree." );
			}
		}
		$tree->oid = $oid;
		return $tree;
	}

	public function insert() {
		return $this->tree[] = new ShellGitTreeEntry;
	}

	public function write() {
		$oid = $this->git->mktree( $this->toString() );
		if ( !$oid ) {
			return false;
		}
		$this->oid = $oid;
		return $this;
	}

	public function toString() {
		$lstree = '';
		foreach ( $this->tree as $entry ) {
			if ( !$entry->isValid() ) {
				throw new Exception( "Cannot string invalid tree" );
			}
			$lstree .= decoct( $entry->getAttributes() );
			$lstree .= ' ';
			$object = $entry->getObject();
			$lstree .= $object->getType();
			$lstree .= ' ';
			$lstree .= $object->getOid();
			$lstree .= '	';
			$lstree .= $entry->getName();
			$lstree .= "\n";
		}
		return $lstree;
	}

	public function __toString() {
		try {
			return $this->toString();
		} catch ( Exception $e ) {
			return "<invalid tree>";
		}
	}

	public function getOid() {
		return $this->oid;
	}

	public function getType() {
		return 'tree';
	}

}

class ShellGitBlob {

	protected $content, $oid;

	public function __construct( $content ) {
		$this->content = $content;
		$this->oid = false;
	}

	public function getContent() {
		return $this->content;
	}

	public function setOid( $oid ) {
		$this->oid = $oid;
	}

	public function getOid() {
		return $this->oid;
	}

	public function getType() {
		return 'blob';
	}

}
class ShellGitOdb {

	protected $git;

	public function __construct( $git ) {
		$this->git = $git;
	}

	public function read( $oid ) {
		$type = $this->git->catFile( 'type', $oid );
		if ( !$type ) {
			return false;
		}
		if ( $type === 'blob' ) {
			$blob = $this->git->catFile( 'blob', $oid );
			if ( $blob ) {
				$blob = new ShellGitBlob( $blob );
				$blob->setOid( $oid );
			}
			return $blob;
		} elseif ( $type === 'tree' ) {
			return ShellGitTree::parse( $this->git, $this, $this->git->lsTree( $oid ), $oid );
		} else {
			throw new Exception( "unknown object type $type" );
		}
	}

	public function hash( $object ) {
		if ( is_string( $object ) ) {
			$object = new ShellGitBlob( $object );
		}
		$oid = $this->git->hashObject( $object, array( 'type' => $object->getType() ) );
		if ( !$oid ) {
			return false;
		}
		$object->setOid( $oid );
		return $object;
	}

	public function write( $object ) {
		if ( is_string( $object ) ) {
			$object = new ShellGitBlob( $object );
		}
		$oid = $this->git->hashObject( $object, array( 'type' => $object->getType(), 'write' => true ) );
		if ( !$oid ) {
			return false;
		}
		$object->setOid( $oid );
		return $object;
	}

	public function createTree() {
		return new ShellGitTree( $this->git, $this );
	}

}

/**
 * Shell based implementation of a Git api
 */
class ShellGit {
	
	protected $path;
	public $odb;

	public function __construct( $path ) {
		$this->path = $path;
		$this->odb = new ShellGitOdb( $this );
	}

	protected function git( $handler, $command, $args = array() ) {

		$cmd = array_merge( array( "git", $command ), $args );
		$cmd = implode( ' ', array_map( 'escapeshellarg', $cmd ) );

		$spec = array(
			0 => array( 'pipe', 'r' ),
			1 => array( 'pipe', 'w' ),
			2 => array( 'pipe', 'w' ),
		);

		$env = array(
			'GIT_DIR' => $this->path,
			// GIT_AUTHOR_NAME, GIT_AUTHOR_EMAIL, GIT_AUTHOR_DATE, GIT_COMMITTER_NAME, GIT_COMMITTER_EMAIL, GIT_COMMITTER_DATE, EMAIL
		);

		$h = proc_open( $cmd, $spec, $pipes, $this->path, $env );
		if ( is_resource( $h ) ) {
			return $handler->handle( $h, $pipes );
		} else {
			throw new Exception( 'Could not open process' );
		}
	}

	public function init() {
		return $this->git( new ShellExitBooleanHandler, 'init', array( '--bare' ) );
	}

	public function lsTree( $tree, array $options = array() ) {
		$args = array();
		// pft, tired of writing handling for args I'll never use

		$args[] = $tree;
		return $this->git( new ShellStdexchangeHandler( false, false ), 'ls-tree', $args );
	}

	public function updateRef( $ref, $newOid, array $options = array() ) {
		$args = array();
		if ( isset( $options['reason'] ) && $options['reason'] ) {
			$args[] = '-m';
			$args[] = $options['reason'];
		}
		if ( !$newOid ) {
			$args[] = '-d';
			$args[] = $ref;
		} else {
			$args[] = $ref;
			$args[] = $newOid;
		}
		if ( isset( $options['old'] ) && $options['old'] ) {
			$args[] = $options['old'];
		}
		return $this->git( new ShellExitBooleanHandler, 'update-ref', $args );
	}

	public function catFile( $mode, $oid, array $options = array() ) {
		$args = array();
		$trim = true;
		switch( $mode ) {
		case 'type': $args[] = '-t'; break;
		case 'size': $args[] = '-s'; break;
		case 'exists': $args[] = '-e'; break;
		case 'prettyprint': $args[] = '-p'; break;
		case 'textconv': $args[] = '--textconv'; break;
		default:
			if ( in_array( $mode, array( 'blob' ) ) ) {
				$args[] = $mode;
				$trim = false; // don't trim raw data
			} else {
				throw new Exception( "Unknown mode $mode" );
			}
			break;
		}
		$args[] = $oid;
		if ( $mode == 'exists' ) {
			$hander = new ShellExitBooleanHandler;
		} else {
			$handler = new ShellStdexchangeHandler( false, $trim );
		}
		return $this->git( $handler, 'cat-file', $args );
	}

	public function hashObject( $object, array $options = array() ) {
		$args = array();
		if ( !isset( $options['type'] ) ) {
			$args[] = '-t';
			$args[] = $options['type'];
		}
		if ( isset( $options['write'] ) && $options['write'] ) {
			$args[] = '-w';
		}
		$args[] = '--stdin';
		return $this->git( new ShellStdexchangeHandler( $object->getContent(), true ), 'hash-object', $args );
	}

	public function mktree( $input, array $options = array() ) {
		$args = array();
		if ( isset( $options['z'] ) && $options['z'] ) {
			$args[] = '-z';
		}
		if ( isset( $options['missing'] ) && $options['missing'] ) {
			$args[] = '--missing';
		}
		if ( isset( $options['batch'] ) && $options['batch'] ) {
			$args[] = '--batch';
		}
		return $this->git( new ShellStdexchangeHandler( $input, true ), 'mktree', $args );
	}

}

/**
 * Git wrapper. Forwards everything to ShellGit
 * This will allow us to dynamically switch to a C++ php extension based implementation
 * with only a simple tweak.
 */
class Git {

	public function __construct( $path ) {
		$this->git = new ShellGit( $path );
		$this->odb = $this->git->odb;
	}

	public function init() {
		return call_user_func_array( array( $this->git, 'init' ), func_get_args() );
	}
	public function lsTree() {
		return call_user_func_array( array( $this->git, 'lsTree' ), func_get_args() );
	}
	public function updateRef() {
		return call_user_func_array( array( $this->git, 'updateRef' ), func_get_args() );
	}
	public function hashObject() {
		return call_user_func_array( array( $this->git, 'hashObject' ), func_get_args() );
	}
	public function mktree() {
		return call_user_func_array( array( $this->git, 'mktree' ), func_get_args() );
	}
	
}
