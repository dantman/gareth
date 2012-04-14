<?php

namespace Gareth\GarethWebBundle\Entity;

use Doctrine\ORM\Mapping as ORM;

/**
 * Gareth\GarethWebBundle\Entity\Remote
 *
 * @ORM\Table()
 * @ORM\Entity
 */
class Remote
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
     * @var Gareth\GarethWebBundle\Entity\Project $project
     *
     * @ORM\ManyToOne(targetEntity="Project", inversedBy="remotes")
     */
    private $project;

    /**
     * @var Gareth\GarethWebBundle\Entity\User $user
     *
     * @ORM\ManyToOne(targetEntity="User", inversedBy="remotes")
     */
    private $user;

    /**
     * @var string $name
     *
     * @ORM\Column(name="name", type="string", length=40)
     */
    private $name;

    /**
     * @var string $url
     *
     * @ORM\Column(name="url", type="string", length=255)
     */
    private $url;


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
     * Set url
     *
     * @param string $url
     */
    public function setUrl($url)
    {
        $this->url = $url;
    }

    /**
     * Get url
     *
     * @return string 
     */
    public function getUrl()
    {
        return $this->url;
    }

    /**
     * Set project
     *
     * @param Gareth\GarethWebBundle\Entity\Project $project
     */
    public function setProject(\Gareth\GarethWebBundle\Entity\Project $project)
    {
        $this->project = $project;
    }

    /**
     * Get project
     *
     * @return Gareth\GarethWebBundle\Entity\Project 
     */
    public function getProject()
    {
        return $this->project;
    }

    /**
     * Set user
     *
     * @param Gareth\GarethWebBundle\Entity\User $user
     */
    public function setUser(\Gareth\GarethWebBundle\Entity\User $user)
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