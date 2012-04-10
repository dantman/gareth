<?php

namespace Gareth\GarethWebBundle\Entity;

use Doctrine\ORM\Mapping as ORM;

/**
 * Gareth\GarethWebBundle\Entity\Identity
 *
 * @ORM\Table()
 * @ORM\Entity
 */
class Identity
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
     * @ORM\ManyToOne(targetEntity="User", inversedBy="identities")
     */
    private $user;

    /**
     * @var string $email
     *
     * @ORM\Column(name="email", type="string", length=255, unique=true)
     */
    private $email;


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