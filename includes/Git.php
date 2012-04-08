<?php

abstract class ShellHandler {

	public function handle( $h, $pipes ) {
		$this->h = $h;
		$this->pipes = $pipes;

		stream_set_blocking( $pipes[1], false );
		stream_set_blocking( $pipes[2], false );

		$result = $this->run();
		return $result;
	}

	public function waitForEnd() {

		// Don't need to write to stdin
		fclose( $this->pipes[0] );

		$err_open = !feof($this->pipes[2]);
		$out_open = !feof($this->pipes[1]);
		while( $err_open || $out_open ) {
			$read = array();
			if ( $err_open ) {
				$read[] = $this->pipes[2];
			}
			if ( $out_open ) {
				$read[] = $this->pipes[1];
			}
			$write = null;
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
			if ( in_array( $this->pipes[1], $read ) ) {
				$chunk = fread( $this->pipes[1], 8192 );
				if ( $chunk === false ) {
					$err_open = false;
				}
				// @todo Do something with this data
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
		$this->waitForEnd();
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

/**
 * Shell based implementation of a Git api
 */
class ShellGit {
	
	public function __construct( $path ) {
		$this->path = $path;
	}

	protected function git( $handler, $porcelain, $args = array() ) {

		$cmd = array_merge( array( "git", $porcelain ), $args );
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

}

/**
 * Git wrapper. Forwards everything to ShellGit
 * This will allow us to dynamically switch to a C++ php extension based implementation
 * with only a simple tweak.
 */
class Git {

	public function __construct( $path ) {
		$this->git = new ShellGit( $path );
	}

	public function __call( $method, $args ) {
		return call_user_func_array( array( $this->git, $method ), $args );
	}
	
}
