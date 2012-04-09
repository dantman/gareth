<?php

namespace Gareth\GarethWebBundle\Libs;

class GarethGit {

	private $path;

	public function __construct( $path ) {
		$this->path = $path;
	}

	public function initialize() {
		return ProcGit::create()
			->setCommand( 'init' )
			->addArg( '--bare' )
			->addArg( '--' )
			->addArg( $this->path )
			->exitOk();
	}

}