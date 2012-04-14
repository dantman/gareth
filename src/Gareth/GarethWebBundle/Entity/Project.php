<?php

namespace Gareth\GarethWebBundle\Entity;

use Doctrine\ORM\Mapping as ORM;
use Symfony\Component\Validator\Constraints as Assert;

/**
 * Gareth\GarethWebBundle\Entity\Project
 *
 * @ORM\Table()
 * @ORM\Entity()
 */
class Project
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
     * @ORM\Column(name="name", type="string", length=255, unique=true)
     * @Assert\Regex("#^\w+(/\w+)*$#")
     * )
     */
    private $name;

    /**
     * @var text $description
     *
     * @ORM\Column(name="description", type="text", nullable=true)
     */
    private $description;

    /**
     * @var array $remotes
     *
     * @ORM\OneToMany(targetEntity="Remote", mappedBy="project", fetch="EXTRA_LAZY")
     */
    private $remotes;


    public function __construct() {
        $this->description = null;
        $this->remotes = new ArrayCollection();
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
     * Set description
     *
     * @param text $description
     */
    public function setDescription($description)
    {
        $this->description = $description;
    }

    /**
     * Get description
     *
     * @return text 
     */
    public function getDescription()
    {
        return $this->description;
    }
    
    /**
     * Add remotes
     *
     * @param Gareth\GarethWebBundle\Entity\Remote $remotes
     */
    public function addRemote(Remote $remotes)
    {
        $this->remotes[] = $remotes;
    }

    /**
     * Get remotes
     *
     * @return Doctrine\Common\Collections\Collection 
     */
    public function getRemotes()
    {
        return $this->remotes;
    }
}