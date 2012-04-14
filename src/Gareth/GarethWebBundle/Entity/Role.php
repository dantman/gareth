<?php

namespace Gareth\GarethWebBundle\Entity;

use Doctrine\ORM\Mapping as ORM;
use Doctrine\Common\Collections\ArrayCollection;
use Symfony\Component\Security\Core\Role\RoleInterface;

/**
 * Gareth\GarethWebBundle\Entity\Role
 *
 * @ORM\Table()
 * @ORM\Entity
 */
class Role implements RoleInterface
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
     * @var string $name
     *
     * @ORM\Column(name="name", type="string", length=30)
     */
    private $name;

    /**
     * @var string $role
     *
     * @ORM\Column(name="role", type="string", length=20, unique=true)
     */
    private $role;

    /**
     * @var array $users
     *
     * @ORM\ManyToMany(targetEntity="User", mappedBy="roles", fetch="EXTRA_LAZY")
     */
    private $users;


    public function __construct()
    {
        $this->users = new ArrayCollection();
    }

    public static function make($role) {
        $r = new Role;
        $r->setRole("ROLE_$role");
        $r->setName(ucfirst(strtolower($role)));
        return $r;
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
     * Set name
     *
     * @param string $name
     */
    public function setName($name)
    {
        $this->name = $name;
    }

    /**
     * Get name
     *
     * @return string 
     */
    public function getName()
    {
        return $this->name;
    }

    /**
     * Set role
     *
     * @param string $role
     */
    public function setRole($role)
    {
        $this->role = $role;
    }

    /**
     * Get role
     *
     * @see RoleInterface
     * @return string 
     */
    public function getRole()
    {
        return $this->role;
    }
    
    /**
     * Add users
     *
     * @param Gareth\GarethWebBundle\Entity\User $users
     */
    public function addUser(User $users)
    {
        $this->users[] = $users;
    }

    /**
     * Get users
     *
     * @return Doctrine\Common\Collections\Collection 
     */
    public function getUsers()
    {
        return $this->users;
    }
}