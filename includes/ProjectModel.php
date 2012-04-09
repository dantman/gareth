<?php

class MysqliProjectModel {

	protected $db;

	public function __construct( $args ) {
		$this->db = $args['db'];
	}

	public function iterateAll() {
		$stmt = $this->db->prepare( "SELECT * FROM projects ORDER BY p_name" );
		return new MysqliModelIterator( $stmt );
	}

	public function getFromName( $name ) {
		$stmt = $this->db->prepare( "SELECT * FROM projects WHERE p_name = ?" );
		$stmt->bind_param( "s", $p_name );
		$p_name = $name;
		$iter = new MysqliModelIterator( $stmt );
		foreach ( $iter as $user ) {
			return $user;
		}
		return false;
	}

	public function insert( $name ) {
		$stmt = $this->db->prepare( "INSERT INTO projects (p_name) VALUES (?)" );
		$stmt->bind_param( "s", $p_name );
		$p_name = $name;
		if ( !$stmt->execute() ) {
			if ( $stmt->error ) {
				throw new Exception( $stmt->error );
			}
			$stmt->close();
			return false;
		}
		$stmt->close();
		return true;
	}

}

class GitProjectModel {

	protected $git;

	public function __construct( $args ) {
		$this->git = $args['git'];
	}

	public function iterateAll() {
		$tree = $this->git->odb->read( 'refs/trees/projects' );
		if ( !$tree ) {
			return new ArrayIterator( array() );
		}
		// return new GitFlatTreeContentsIterator( $tree );
	}

	public function getFromName( $name ) {
		return false;
	}

	public function insert( $name ) {
		$odb = $this->git->odb;

		if ( preg_match( '!/!', $name ) ) {
			throw new Exception( 'Recurse tree not implemented yet.' );
		}

		$tree = $odb->createTree();

		$entry = $tree->insert();
		$entry->setName( $name );
		$entry->setObject( $odb->write( json_encode( array( 'name' => $name ) ) ) );

		$tree = $tree->write();

		$this->git->updateRef( 'refs/trees/projects', $tree->getOid() );

	}

}

abstract class ProjectModel {

	public static $singleton = null;

	public static function singleton() {
		if ( !self::$singleton ) {
			$className = Config::getModelClass( 'ProjectModel' );
			self::$singleton = new $className( Config::getModelArgs() );
		}
		return self::$singleton;
	}
	
	public static function __callStatic( $name, $args ) {
		return call_user_func_array( array( self::singleton(), $name ), $args );
	}
}
