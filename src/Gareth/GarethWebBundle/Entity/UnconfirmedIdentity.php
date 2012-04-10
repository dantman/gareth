<?php

namespace Gareth\GarethWebBundle\Entity;

use Doctrine\ORM\Mapping as ORM;

/**
 * Gareth\GarethWebBundle\Entity\UnconfirmedIdentity
 *
 * @ORM\Table()
 * @ORM\Entity
 */
class UnconfirmedIdentity
{
    /**
     * @var integer $id
     *
     * @ORM\Column(name="id", type="integer")
     * @ORM\Id
     * @ORM\GeneratedValue(strategy="AUTO")
     */
    private $id;

    /**
     * @var Gareth\GarethWebBundle\Entity\User $user
     *
     * @ORM\ManyToOne(targetEntity="User", inversedBy="unconfirmed_identities")
     */
    private $user;

    /**
     * @var string $email
     *
     * @ORM\Column(name="email", type="string", length=255)
     */
    private $email;

    /**
     * @var string $token
     *
     * @ORM\Column(name="token", type="string", length=64)
     */
    private $token;


    /**
     * Get id
     *
     * @return integer 
     */
    public function getId()
    {
        return $this->id;
    }

    /**
     * Set email
     *
     * @param string $email
     */
    public function setEmail($email)
    {
        $this->email = $email;
    }

    /**
     * Get email
     *
     * @return string 
     */
    public function getEmail()
    {
        return $this->email;
    }

    /**
     * Set token
     *
     * @param string $token
     */
    public function setToken($token)
    {
        $this->token = $token;
    }

    /**
     * Get token
     *
     * @return string 
     */
    public function getToken()
    {
        return $this->token;
    }

    /**
     * Set user
     *
     * @param Gareth\GarethWebBundle\Entity\User $user
     */
    public function setUser(User $user)
    {
        $this->user = $user;
    }

    /**
     * Get user
     *
     * @return Gareth\GarethWebBundle\Entity\User 
     */
    public function getUser()
    {
        return $this->user;
    }
}