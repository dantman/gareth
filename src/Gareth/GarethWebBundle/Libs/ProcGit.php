<?php

namespace Gareth\GarethWebBundle\Libs;

use Symfony\Component\Process\Process;
use Symfony\Component\Process\ProcessBuilder;

class ProcGit {

	private $gitDir = null;
	private $command = null;
	private $args = array();

	private $builder, $proc;
	public function __construct() {
		$this->builder = new ProcessBuilder( array( 'git' ) );
	}

	public static function create() {
		return new static;
	}

	public function setGitDir( $gitDir ) {
		$this->gitDir = $gitDir;
		return $this;
	}

	public function setCommand( $command ) {
		$this->command = $command;
		return $this;
	}

	public function addArg( $arg ) {
		$this->arg[] = $arg;
		return $this;
	}

	/** Execution methods **/

	private function run() {
		if ( isset( $this->proc ) ) {
			return $this->proc;
		}
		$this->builder->inheritEnvironmentVariables( false );
		$this->builder->setEnv( 'GIT_DIR', $this->gitDir );
		$this->builder->add( $this->command );
		foreach ( $this->arg as $arg ) {
			$this->builder->add( $arg );
		}

		$this->proc = $this->builder->getProcess();

		$this->proc->run( function( $type, $data ) {
			// For some reason PHP throws fatals saying it can't find Process::ERR
			// even though it is defined
			if ( $type == 'err' ) {
				trigger_error( "git stderr: $data", E_USER_WARNING );
			}
		} );

		return $this->proc;
	}


	/**
	 * Wait till the program exits and then return the exit code.
	 */
	public function exitCode() {
		return $this->run()->getExitCode();
	}

	/**
	 * Wait till the program exits and then return a boolean based on the exit code:
	 *   0 = true
	 *   * = false
	 */
	public function exitOk() {
		return $this->run()->isSuccessful();
	}

}
