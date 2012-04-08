<?php

class ProjectModelIterator extends IteratorIterator {

	public function current() {
		return Project::newFromRow( parent::current() );
	}

}

class Project {
	
	protected $name, $description;

	public static function iterate() {
		return new ProjectModelIterator( ProjectModel::iterateAll() );
	}

	public static function newFromName( $name ) {
		return self::newFromRow( ProjectModel::getFromName( $name ) );
	}

	public static function newFromRow( $row ) {
		if ( !$row ) {
			return null;
		}
		$project = new self;
		$project->name = $row->p_name;
		$project->description = $row->p_description;
		return $project;
	}

	public static function create( $name ) {
		if ( !preg_match( '#^\w+(/w+)*(\.git)?$#', $name ) ) {
			throw new Exception( 'Invalid project name.' );
		}
		$name = preg_replace( '/\.git$/', '', $name );

		if ( self::newFromName( $name ) ) {
			throw new Exception( 'A repo with that name already exists.' );
		}

		# Initialize the repo
		$path = Config::getRepoPath( $name );
		if ( !is_dir( $path ) ) {
			if ( !mkdir( $path, 0777, true ) ) {
				trigger_error( "Could not create path $path." );
			}
		}
		$repo = new Git( $path );
		if ( !$repo->init() ) {
			throw new Exception( 'Repository could not be initialized.' );
		}

		# Add the project to the database
		ProjectModel::insert( $name );
		return self::newFromName( $name );
	}

	public function getName() {
		return $this->name;
	}

	public function getDescription() {
		return $this->description;
	}

}