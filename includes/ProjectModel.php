<?php

class MysqliModelIterator implements Iterator {

	protected $stmt, $position, $valid, $fetched, $resultArray;

	public function __construct( $stmt ) {
		$this->stmt = $stmt;

		// Examine the metadata and use it to create a set of variables that
		// will make a keyed array bindable to the statement
		$this->resultArray = array();
		$metadata = $this->stmt->result_metadata();
		$fields = $metadata->fetch_fields();
		foreach( $fields as $field ) {
			$result[$field->name] = "";
			$this->resultArray[$field->name] = &$result[$field->name];
		}

		// Bind the indexed array to the statement
		call_user_func_array( array( $this->stmt, 'bind_result' ), $this->resultArray);
	}

	public function rewind() {
		$this->position = 0;
		$this->valid = false;
		$this->fetched = false;
		if ( !$this->stmt->execute() ) {
			throw new Exception( $this->stmt->error );
		}
	}

	public function valid() {
		if ( !$this->fetched ) {
			$fetch = $this->stmt->fetch();
			$this->fetched = true;
			if ( $fetch === false ) {
				$this->stmt->close();
				throw new Exception( $this->stmt->error );
			} elseif ( $fetch === null ) {
				$this->stmt->close();
				$this->valid = false;
			} else {
				$this->valid = true;
			}
		}
		return $this->valid;
	}

	public function next() {
		$this->fetched = false;
		$this->position++;
	}

	public function key() {
		return $this->position;
	}

	public function current() {
		// Use the keyed array to create an object
		$resultObject = new stdClass();
		foreach( $this->resultArray as $key => $value ) {
			$resultObject->{$key} = $value;
		}
		return $resultObject;
	}

}

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
		if ( !$stmt->execute() ) {
			throw new Exception( $stmt->error );
		}

		// Examine the metadata and use it to create a set of variables that
		// will make a keyed array bindable to the statement
		$resultArray = array();
		$metadata = $stmt->result_metadata();
		$fields = $metadata->fetch_fields();
		foreach( $fields as $field ) {
			$result[$field->name] = "";
			$resultArray[$field->name] = &$result[$field->name];
		}

		// Bind the indexed array to the statement
		call_user_func_array( array( $stmt, 'bind_result' ), $resultArray);

		$fetch = $stmt->fetch();
		if ( $fetch === false ) {
			$stmt->close();
			throw new Exception( $stmt->error );
		}
		if ( $fetch === null ) {
			$stmt->close();
			return false;
		}
		// Use the keyed array to create an object
		$resultObject = new stdClass();
		foreach( $resultArray as $key => $value ) {
			$resultObject->{$key} = $value;
		}

		$stmt->close();

		return $resultObject;
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

abstract class ProjectModel {

	public static $singleton = null;

	public static function singleton() {
		if ( !self::$singleton ) {
			self::$singleton = new MysqliProjectModel( Config::getModelArgs() );
		}
		return self::$singleton;
	}
	
	public static function __callStatic( $name, $args ) {
		return call_user_func_array( array( self::singleton(), $name ), $args );
	}
}
