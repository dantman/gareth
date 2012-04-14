<?php

namespace Gareth\GarethWebBundle\Controller;

use Gareth\GarethWebBundle\Entity\User;
use Gareth\GarethWebBundle\Entity\Identity;
use Gareth\GarethWebBundle\Entity\UnconfirmedIdentity;
use Gareth\GarethWebBundle\Libs\CryptRand;

use Symfony\Bundle\FrameworkBundle\Controller\Controller;
use Symfony\Component\HttpFoundation\Request;

use JMS\SecurityExtraBundle\Annotation\Secure;

class SettingsController extends Controller
{
    
    /**
     * @Secure(roles="ROLE_USER")
     */
    public function profileAction(Request $request)
    {
        $user = $this->get('security.context')->getToken()->getUser();

		return $this->render('GarethBundle:Settings:profile.html.twig', array(
            'user' => $user,
		));
    }

    /**
     * @Secure(roles="ROLE_USER")
     */
    public function identitiesAction(Request $request)
    {
        $user = $this->get('security.context')->getToken()->getUser();

        $identity = new UnconfirmedIdentity;
        $identity->setUser( $user );
        $form = $this->createFormBuilder($identity)
            ->add('email', 'email')
            ->getForm();

        if ( $request->getMethod() == 'POST' ) {
            $form->bindRequest($request);
            if ( $form->isValid() ) {
                $unconfirmedIdentities = $user->getUnconfirmedIdentities();
                $email = $identity->getEmail();
                if ( !$unconfirmedIdentities->exists( function( $k, $i ) use( $email ) { return $i->getEmail() == $email; } ) ) {
                    $identity->setToken( CryptRand::generateHex( 64 ) );
                    $unconfirmedIdentities->add( $identity );

                    // Insert identity into database
                    $em = $this->getDoctrine()->getEntityManager();
                    $em->persist($identity);
                    $em->persist($user);
                    $em->flush();
                }

                return $this->redirect($this->generateUrl('identities'));
            }
        }

		return $this->render('GarethBundle:Settings:identities.html.twig', array(
            'user' => $user,
            'identities' => $user->getIdentities(),
            'unconfirmed_identities' => $user->getUnconfirmedIdentities(),
            'add_form' => $form->createView(),
		));
    }

    /**
     * @Secure(roles="ROLE_USER")
     */
    public function remotesAction(Request $request)
    {
        $user = $this->get('security.context')->getToken()->getUser();

        return $this->render('GarethBundle:Settings:remotes.html.twig', array(
            'user' => $user,
        ));
    }

}
