<?php

namespace Gareth\GarethWebBundle\Controller;

use Gareth\GarethWebBundle\Entity\Project;
use Gareth\GarethWebBundle\Libs\GarethGit;

use Symfony\Bundle\FrameworkBundle\Controller\Controller;
use Symfony\Component\HttpFoundation\Request;


class ProjectController extends Controller
{

    public function indexAction()
    {
		$projects = $this->getDoctrine()
			->getRepository('GarethBundle:Project')
			->findAll();
        return $this->render('GarethBundle:Project:index.html.twig', array('projects' => $projects));
    }

    public function showAction($name)
    {
		$project = $this->getDoctrine()
			->getRepository('GarethBundle:Project')
			->findOneByName($name);
        return $this->render('GarethBundle:Project:show.html.twig', array('project' => $project));
    }

    public function createAction( Request $request )
    {
    	$project = new Project;

    	$form = $this->createFormBuilder($project)
    		->add('name', 'text')
    		->add('description', 'text', array('required' => false))
    		->getForm();

		if ( $request->getMethod() == 'POST' ) {
			$form->bindRequest($request);
			if ( $form->isValid() ) {
                // Initialize a git repo
                $repo_path = $this->container->getParameter('gareth.repo_path');
                $git_class = $this->container->getParameter('gareth.git_class');
                $git = new $git_class( rtrim( $repo_path, '/' ) . '/' . $project->getName() . '.git' );
                $git->initialize();

                // Insert project into database
				$em = $this->getDoctrine()->getEntityManager();
				$em->persist($project);
				$em->flush();

				return $this->redirect($this->generateUrl('project', array('name' => $project->getName())));
			}
		}

        return $this->render('GarethBundle:Project:create.html.twig', array(
        	'form' => $form->createView(),
        ));
    }
}
