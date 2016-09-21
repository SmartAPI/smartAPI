<?php

$infile = "allbiotools.json";
$list = json_decode(file_get_contents($infile), true);

$outfile = "/code/smartAPI/repository-ui/es/biotools.es.json";
$fout = fopen($outfile,"w");

//file_put_contents("biotools.pretty.json", json_encode($obj, JSON_PRETTY_PRINT));
foreach($list AS $k => $v) {
	$keep = false;
	foreach($v['resourceType'] AS $type) {
		if($type == "Tool") {$keep = true;break;}
	}
	if($keep !== true) continue;
		
	
	$api = new stdClass;
	$info = new stdClass;
	$info->title = $v['name'];
	if(isset($v['version'])) $info->version = $v['version'];
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
	
