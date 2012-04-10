<?php

namespace Gareth\GarethWebBundle\Entity;

use Doctrine\ORM\Mapping as ORM;
use Doctrine\Common\Collections\ArrayCollection;
use Symfony\Component\Security\Core\User\UserInterface;

/**
 * Gareth\GarethWebBundle\Entity\User
 *
 * @ORM\Table()
 * @ORM\Entity(repositoryClass="Gareth\GarethWebBundle\Entity\UserRepository")
 */
class User implements UserInterface
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
     * @var string $username
     *
     * @ORM\Column(name="username", type="string", length=255, unique=true)
     */
    private $username;

    /**
     * @var string $salt
     *
     * @ORM\Column(name="salt", type="string", length=32)
     */
    private $salt;

    /**
     * @var string $password
     *
     * @ORM\Column(name="password", type="string", length=40)
     */
    private $password;

    /**
     * @var array $identities
     *
     * @ORM\OneToMany(targetEntity="Identity", mappedBy="user")
     */
    private $identities;

    /**
     * @var array $unconfirmed_identities
     *
     * @ORM\OneToMany(targetEntity="UnconfirmedIdentity", mappedBy="user")
     */
    private $unconfirmed_identities;


    public function __construct()
    {
        // FIXME? This is an insecure salt, it should be generated with a cryptographic source.
        // Then agian, our goal is to use LDAP in the end.
        $this->salt = md5(uniqid(null, true));
        $this->identities = new ArrayCollection();
    }

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
     * Set username
     *
     * @param string $username
     */
    public function setUsername($username)
    {
        $this->username = $username;
    }

    /**
     * Get username
     *
     * @return string 
     * @inheritDoc
     */
    public function getUsername()
    {
        return $this->username;
    }

    /**
     * Set salt
     *
     * @param string $salt
     */
    public function setSalt($salt)
    {
        $this->salt = $salt;
    }

    /**
     * Get salt
     *
     * @return string 
     * @inheritDoc
     */
    public function getSalt()
    {
        return $this->salt;
    }

    /**
     * Set password
     *
     * @param string $password
     */
    public function setPassword($password)
    {
        $this->password = $password;
    }

    /**
     * Get password
     *
     * @return string 
     * @inheritDoc
     */
    public function getPassword()
    {
        return $this->password;
    }
    /**
     * @inheritDoc
     */
    public function getRoles()
    {
        return array('ROLE_USER');
    }

    /**
     * @inheritDoc
     */
    public function eraseCredentials()
    {
    }

    /**
     * @inheritDoc
     */
    public function equals(UserInterface $user)
    {
        return $this->username === $user->getUsername();
    }

    /**
     * Add identities
     *
     * @param Gareth\GarethWebBundle\Entity\Identity $identities
     */
    public function addIdentity(Identity $identities)
    {
        $this->identities[] = $identities;
    }

    /**
     * Get identities
     *
     * @return Doctrine\Common\Collections\Collection 
     */
    public function getIdentities()
    {
        return $this->identities;
    }

    /**
     * Add unconfirmed_identities
     *
     * @param Gareth\GarethWebBundle\Entity\UnconfirmedIdentity $unconfirmedIdentities
     */
    public function addUnconfirmedIdentity(UnconfirmedIdentity $unconfirmedIdentities)
    {
        $this->unconfirmed_identities[] = $unconfirmedIdentities;
    }

    /**
     * Get unconfirmed_identities
     *
     * @return Doctrine\Common\Collections\Collection 
     */
    public function getUnconfirmedIdentities()
    {
        return $this->unconfirmed_identities;
    }
}