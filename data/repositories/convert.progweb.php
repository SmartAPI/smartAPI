<?php

$infile = "progWeb.csv";
$fin = fopen($infile,"r");
$header =  fgetcsv($fin,0,"\t");

$outfile = "/code/smartAPI/repository-ui/es/pw.es.json";
$fout = fopen($outfile,"w");

/*
	[0] => #
    [1] => API Endpoint
    [2] => API Forum
    [3] => API Homepage
    [4] => API Kits
    [5] => API Provider
    [6] => Authentication Mode
    [7] => Console URL
    [8] => Contact Email
    [9] => Developer Support
    [10] => Differentiators
    [11] => Name
    [12] => Other options
    [13] => Primary Category
    [14] => Protocol / Formats
    [15] => Related to?
    [16] => SSL Support
    [17] => Secondary Categories
    [18] => Twitter Url
    [19] => link
*/
while($a = fgetcsv($fin,0,"\t")) {
	if(count($a) != 20) {
		trigger_error("Found ".count($a)." rows instead of 20");
		exit;
	}
	
	$api = new stdClass;
	$info = new stdClass;
	$info->title = $a[11];
	
	echo $a[10].PHP_EOL;continue;
	if(isset($v['description'])) $info->description = $v['description'];
	if(isset($v['license'])) $info->termsOfService = $v['license'];
	if(isset($v['homepage'])) $info->homepage = $v['homepage'];
	if(isset($v['topic'])) {
		foreach($v['topic'] AS $topic) {
			$keyword = new stdClass;
			$keyword->name = $topic['term'];
			if(isset($topic['uri'])) $keyword->uri = $topic['uri'];
			
			$api->tags[] = $keyword;
	}}
	
	$api->info = $info;
	$id = "tools_".($k+1);
	
	fwrite($fout, '{"index":{"_index":"smartapi","_type":"api","_id":"'.$id.'"}}'.PHP_EOL);
	fwrite($fout, json_encode($api).PHP_EOL);
	
	
}
fclose($fout);exit;
	
