<?php

namespace Gareth\GarethWebBundle\Controller;

use Gareth\GarethWebBundle\Entity\Project;

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
    		->add('description', 'text')
    		->getForm(); 

		if ( $request->getMethod() == 'POST' ) {
			$form->bindRequest($request);
			if ( $form->isValid() ) {
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
