<?php
/**
 * This defines the framework's autoloading handler
 *
 * @file
 */

/**
 * Locations of core classes
 * Extension classes are specified with $wgAutoloadClasses
 * This array is a global instead of a static member of AutoLoader to work around a bug in APC
 */
global $MFrameAutoloadClasses;

$MFrameAutoloadClasses = array(
	# Includes
	'MFrameCryptRand' => 'includes/CryptRand.php',
	'MFrameHtml' => 'includes/Html.php',
	'MFrameIP' => 'includes/IP.php',
	'MFramePathRouter' => 'includes/PathRouter.php',
	'MFramePathRouterPatternReplacer' => 'includes/PathRouter.php',
	'MFrameWebRequest' => 'includes/WebRequest.php',
	'MFrameWebRequestUpload' => 'includes/WebRequest.php',
	'MFrameWebResponse' => 'includes/WebResponse.php',

	# includes/db
	'MFrameBlob' => 'includes/db/DatabaseUtility.php',
	'MFrameChronologyProtector' => 'includes/db/LBFactory.php',
	'MFrameCloneDatabase' => 'includes/db/CloneDatabase.php',
	'MFrameDatabase' => 'includes/db/DatabaseMysql.php',
	'MFrameDatabaseBase' => 'includes/db/Database.php',
	'MFrameDatabaseIbm_db2' => 'includes/db/DatabaseIbm_db2.php',
	'MFrameDatabaseMssql' => 'includes/db/DatabaseMssql.php',
	'MFrameDatabaseMysql' => 'includes/db/DatabaseMysql.php',
	'MFrameDatabaseOracle' => 'includes/db/DatabaseOracle.php',
	'DatabasePostgres' => 'includes/db/DatabasePostgres.php',
	'DatabaseSqlite' => 'includes/db/DatabaseSqlite.php',
	'DatabaseSqliteStandalone' => 'includes/db/DatabaseSqlite.php',
	'DatabaseType' => 'includes/db/Database.php',
	'DBConnectionError' => 'includes/db/DatabaseError.php',
	'DBError' => 'includes/db/DatabaseError.php',
	'DBObject' => 'includes/db/DatabaseUtility.php',
	'DBMasterPos' => 'includes/db/DatabaseUtility.php',
	'DBQueryError' => 'includes/db/DatabaseError.php',
	'DBUnexpectedError' => 'includes/db/DatabaseError.php',
	'FakeResultWrapper' => 'includes/db/DatabaseUtility.php',
	'Field' => 'includes/db/DatabaseUtility.php',
	'IBM_DB2Blob' => 'includes/db/DatabaseIbm_db2.php',
	'IBM_DB2Field' => 'includes/db/DatabaseIbm_db2.php',
	'LBFactory' => 'includes/db/LBFactory.php',
	'LBFactory_Multi' => 'includes/db/LBFactory_Multi.php',
	'LBFactory_Simple' => 'includes/db/LBFactory.php',
	'LBFactory_Single' => 'includes/db/LBFactory_Single.php',
	'LikeMatch' => 'includes/db/DatabaseUtility.php',
	'LoadBalancer' => 'includes/db/LoadBalancer.php',
	'LoadBalancer_Single' => 'includes/db/LBFactory_Single.php',
	'LoadMonitor' => 'includes/db/LoadMonitor.php',
	'LoadMonitor_MySQL' => 'includes/db/LoadMonitor.php',
	'LoadMonitor_Null' => 'includes/db/LoadMonitor.php',
	'MySQLField' => 'includes/db/DatabaseMysql.php',
	'MySQLMasterPos' => 'includes/db/DatabaseMysql.php',
	'ORAField' => 'includes/db/DatabaseOracle.php',
	'ORAResult' => 'includes/db/DatabaseOracle.php',
	'PostgresField' => 'includes/db/DatabasePostgres.php',
	'ResultWrapper' => 'includes/db/DatabaseUtility.php',
	'SQLiteField' => 'includes/db/DatabaseSqlite.php',
);

class MFrameAutoLoader {
	/**
	 * autoload - take a class name and attempt to load it
	 *
	 * @param $className String: name of class we're looking for.
	 * @return bool Returning false is important on failure as
	 * it allows Zend to try and look in other registered autoloaders
	 * as well.
	 */
	static function autoload( $className ) {
		global $MFrameAutoloadClasses;

		if ( isset( $MFrameAutoloadClasses[$className] ) ) {
			$filename = $MFrameAutoloadClasses[$className];
		} else {
			if ( function_exists( 'wfDebug' ) ) {
				wfDebug( "Class {$className} not found; skipped loading\n" );
			}

			# Give up
			return false;
		}

		# Make an absolute path, this improves performance by avoiding some stat calls
		if ( substr( $filename, 0, 1 ) != '/' && substr( $filename, 1, 1 ) != ':' ) {
			global $MFramePath;
			$filename = "$MFramePath/$filename";
		}

		require( $filename );

		return true;
	}

	/**
	 * Force a class to be run through the autoloader, helpful for things like
	 * Sanitizer that have define()s outside of their class definition. Of course
	 * this wouldn't be necessary if everything in MediaWiki was class-based. Sigh.
	 *
	 * @return Boolean Return the results of class_exists() so we know if we were successful
	 */
	static function loadClass( $class ) {
		return class_exists( $class );
	}
}

spl_autoload_register( array( 'MFrameAutoLoader', 'autoload' ) );
