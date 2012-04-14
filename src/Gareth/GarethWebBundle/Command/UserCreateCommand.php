<?php

namespace Gareth\GarethWebBundle\Command;

use Symfony\Bundle\FrameworkBundle\Command\ContainerAwareCommand;
use Symfony\Component\Console\Input\InputOption;
use Symfony\Component\Console\Input\InputArgument;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Output\OutputInterface;

use Gareth\GarethWebBundle\Entity\User;
use Gareth\GarethWebBundle\Entity\Role;

class UserCreateCommand extends ContainerAwareCommand
{

	protected function configure()
	{
		$this
			->setName('gareth:user:create')
			->setDescription("Create a new user in the Gareth database.")
			->addArgument('username', InputArgument::REQUIRED, "The user's username.")
			->addArgument('password', InputArgument::REQUIRED, "The user's password.")
			->addOption('admin', 'a', InputOption::VALUE_NONE, 'Make this user an admin?')
		;
	}

	protected function execute(InputInterface $input, OutputInterface $output)
	{
		$container = $this->getContainer();
		$em = $container->get('doctrine')->getEntityManager();

		$user = new User;
		$user->setUsername( $input->getArgument('username') );

		// Encode password
		$encoderFactory = $container->get('security.encoder_factory');
		$encoder = $encoderFactory->getEncoder($user);
		$user->setPassword( $encoder->encodePassword( $input->getArgument('password'), $user->getSalt() ) );

		// Add ROLE_ADMIN if told to
		if ( $input->getOption('admin') ) {
			$user->addRole( $role = Role::make('ADMIN') );
			$em->persist( $role );
		}
		
		$em->persist($user);
		$em->flush();
		$output->writeln("User created.");
	}

}