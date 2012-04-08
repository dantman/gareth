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
