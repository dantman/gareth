<?php

class MysqliUserModel {

	protected $db;

	public function __construct( $args ) {
		$this->db = $args['db'];
	}

	public function getFromID( $id ) {
		$stmt = $this->db->prepare( "SELECT * FROM users WHERE u_id = ?" );
		$stmt->bind_param( "i", $u_id );
		$u_id = $id;
		$iter = new MysqliModelIterator( $stmt );
		foreach ( $iter as $user ) {
			return $user;
		}
		return false;
	}

}

class User {

	protected $id, $type, $key;

	public static function newFromRow( $row ) {
		if ( !$row ) {
			return null;
		}
		$project = new self;
		$project->id = $row->p_id;
		$project->type = $row->p_type;
		$project->key = $row->p_key;
		return $project;
	}

}
