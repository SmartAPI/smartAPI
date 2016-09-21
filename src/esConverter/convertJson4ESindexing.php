<?php

if($argc !== 2) {
	echo("usage: php convertJson4ESindexing.php [filename or uri]");
	exit;
}

$file = $argv[1];
if(strstr($file,"http") !== FALSE) {
	// retrieve the file
	$buf = file_get_contents($file);
	if($buf === FALSE or $buf == '') {
		trigger_error("No document found at $file", E_USER_ERROR);
		exit;
	}
} else {
	if (file_exists($file)) {
		$buf = file_get_contents($file);
		if($buf === FALSE or $buf == '') {
			trigger_error("No content in $file", E_USER_ERROR);
			exit;
		}
	} else {
		trigger_error("No file found: $file", E_USER_ERROR);
		exit;
	}
}

// now process the file
$json = json_decode($buf, true);

// process each pathinfo
unset($operations);
if(isset($json['paths'])) {
	foreach($json['paths'] AS $path => $path_object) {
		foreach($path_object AS $http_operation => $operation) {
			$operation['path'] = $path;
			$operation['httpOperation'] = $http_operation;
			
			// process responses
			unset($responses);
			if(isset($operation['responses'])) {
				foreach($operation['responses'] AS $http_operation => $response) {
					$response['httpCode'] = $http_operation;
					if(isset($response['schema'])) unset($response['schema']); // optional for now.
					$responses[] = $response;
				}
				unset($operation['responses']);
				$operation['responses'] = $responses;
			}

			// add the object to the stack
			$operations[] = $operation;			
		}
	}
}
if(isset($operations)) {
	unset($json['paths']);
	$json['operations'] = $operations; 
}



$buf = json_encode($json, JSON_PRETTY_PRINT);
echo $buf;




