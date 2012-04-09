<?php

namespace Gareth\GarethWebBundle\DependencyInjection;

use Symfony\Component\Config\Definition\Builder\TreeBuilder;
use Symfony\Component\Config\Definition\ConfigurationInterface;

/**
 * This is the class that validates and merges configuration from your app/config files
 *
 * To learn more see {@link http://symfony.com/doc/current/cookbook/bundles/extension.html#cookbook-bundles-extension-config-class}
 */
class Configuration implements ConfigurationInterface
{
    /**
     * {@inheritDoc}
     */
    public function getConfigTreeBuilder()
    {
        $treeBuilder = new TreeBuilder();
        $rootNode = $treeBuilder->root('gareth');

        $rootNode
            ->children()
                ->scalarNode('repo_path')->isRequired()->end()
                ->scalarNode('git_class')->defaultValue('Gareth\GarethWebBundle\Libs\GarethGit')->end()
                ->booleanNode('test')->end()
            ->end()
        ;

        return $treeBuilder;
    }
}
