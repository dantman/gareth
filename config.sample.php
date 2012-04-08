<?php

class Config {

	public static function getRepoPath( $name ) {
		return '/absolute/path/' . $name . '.git';
	}

	public static function getModelArgs() {
		static $singleton = null;
		if ( !$singleton ) {
			$singleton = array(
				'db' => new mysqli( 'localhost', '<user>', '<password>', '<database>' ),
			);
		}
		return $singleton;
	}

}