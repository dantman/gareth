<?php

namespace Gareth\GarethWebBundle\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\Controller;


class DefaultController extends Controller
{
    
    public function indexAction($name)
    {
        return $this->render('GarethBundle:Default:index.html.twig', array('name' => $name));
    }
}
