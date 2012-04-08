<?php

$MFramePath = __DIR__ . '/framework';
require_once( "$MFramePath/includes/AutoLoader.php" );
require_once( __DIR__ . "/includes/AutoLoader.php" );

require_once( __DIR__ . '/config.php' );

$request = new MFrameWebRequest;
$router = new MFramePathRouter;
# Projects list and individual project pages
$router->addStrict( '/projects', array( '$' => 'projects', 'action' => 'list' ) );
$router->addStrict( '/projects/$1', array( '$' => 'projects', 'action' => 'show', 'project' => '$1' ) );
$router->addStrict( '/projects/create', array( '$' => 'projects', 'action' => 'create' ) );

$route = $router->parse( preg_replace( '/[?#].*$/', '', $request->getRequestURL() ) );
switch( @$route['$'] ) {
case 'projects':
	switch( @$route['action'] ) {
	case 'create':
		if ( $request->wasPosted() ) {
			Project::create( $request->getVal( 'name' ) );
		}
		# $view = new View( 'projects/create/form' );
		# $view->render();
		?>
<form action="/projects/create" method="POST">
	<input name="name" value="">
	<input type="submit" value="Create">
</form>
<?php
		break;
	case 'show':
		$project = Project::newFromName( $route['project'] );
		if ( !$project ) {
			echo "There is no project by the name '" . htmlspecialchars( $route['project'] ) . "'.";
		} else { ?>
<h1>Project <?= htmlspecialchars( $project->getName() ); ?></h1>
<div class="project-description"><?= htmlspecialchars( $project->getDescription() ); ?></div>
<?php
		}
		break;
	default: ?>
<table>
	<thead>
		<tr>
			<th>Project Name</th>
			<th>Project Description</th>
		</tr>
	</thead>
	<tbody>
<?php
		foreach ( Project::iterate() as $project ) { ?>
		<tr>
			<td><a href="/projects/<?= htmlspecialchars( $project->getName() ); ?>"><?= htmlspecialchars( $project->getName() ); ?></a></td>
			<td><?= htmlspecialchars( $project->getDescription() ); ?></td>
		</tr>
<?php
		} ?>
	</tbody>
</table>
<?php
		break;
	}
	break;

}