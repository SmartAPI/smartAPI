<template>
  <main id="dashApp" style="padding-top:20px;min-height:90vh;" class="blue-grey darken-3" v-cloak>
    <!-- IF NO USER INFO DISPLAY LOGIN-->
    <div v-if="!loggedIn" class="padding20 card-panel white center-align">
        <h5 class="text_h3 blue-grey-text-text">
        You Must Be Signed In To Use Your Dashboard
        </h5>
        <a href="/oauth" class="btn green">
        Login
        </a>
    </div>
    <!-- LOADING -->
    <div v-if="loading" id="loading-overlay" class="center-align" style="background-color: rgba(18, 52, 84, 0.5); cursor: default;">
        <div class="center-align" style="padding-top: 300px;">
        <Image img_width="100px"  alt="Loading" img_name="fly.gif" class=""></Image>
        <h3 class="white-text logoFont">Loading...</h3>
        </div>
    </div>
    <!-- Loading END -->
    <!-- IF USER INFO DISPLAY DASHBOARD -->
    <div id="tippyParent" v-if="loggedIn" class="row" style="margin-bottom: 0; width: 100%;min-height:70vh;">
        <div class="col s12 padding20 blue">
            <div class="dashboard-header blue">
                <Image 
                id="dashboardPhoto" 
                img_width="100px" 
                :img_name="'user-default.png'" 
                class="responsive-img circle dash-photo" 
                :alt="userInfo.login"></Image>
                <div>
                    <h5 v-if="userInfo?.name" class="white-text">Hello, {{ userInfo?.name.split(" ")[0] || userInfo.login }}!</h5>
                    <p><a target="_blank" class="white-text" :href="'https://github.com/'+userInfo.login"><i class="tiny fa fa-github-alt white-text"></i> {{userInfo.login}}</a></p>
                </div>
                <div class="center-align white-text">
                    <b v-text="'APIs Registered: '+total"></b>
                </div>
            </div>
        </div>
        <div class="col s12 center-align">
            <div class="container row" style="margin:auto;">
            <div class="p-1 col s12">
                <input v-model='searchQuery' placeholder="Search by API name" type="text" class="browser-default margin20 blue-grey darken-3 l-blue-text lighter" style="width: 40%; outline: none; padding: 10px; border-radius: 20px; border:var(--blue-light) 2px solid;"/>
            </div>

            <div class="col s12 card-panel">
                <table class="striped highlight responsive-table">
                <thead>
                    <tr class="grey-text">
                        <th>Name</th>
                        <th>Last Updated</th>
                        <th>Refresh</th>
                        <th>Validate</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(api,index) in results" :key="index">
                    <td>
                        <h6 class="left-align">
                        <b>{{ api.info.title }}</b>
                        <small>
                            <span class="grey-text">V.{{api.info.version}}</span>
                        </small>
                        <small v-if="api?.openapi" class="green-text">
                            OAS3
                        </small>
                        <small v-else-if="api?.swagger" class="blue-text">
                            Swagger2
                        </small>
                        <a href="#modal2" class="modal-trigger" @click="getDetails(index)">
                            <small><i class="tiny material-icons">settings</i> Settings</small>
                        </a>
                        </h6>
                        
                    </td>
                    <td>
                        <small>
                        <b class="green-text"> {{ convertDate(api._meta.last_updated) }}</b>
                        </small>
                    </td>
                    <td>
                        <button type="button" class="btn btn-small tipped green scale-in-center" data-tippy-info="<b class='green-text'>Refresh</b> <br/>(Manually update API metadata when a valid change is detected)" 
                        @click="refreshThis(api.info.title,api._id);">
                        <i class=" material-icons white-text">refresh</i>
                        </button>
                    </td>
                    <td>
                        <button type="button" @click="validate(api._meta.url)" class="btn btn-small scale-in-center indigo white-text tipped"
                            data-tippy-info="<b class='indigo-text'>Validate Only</b> <br/>(Validate latest API metadata from the source URL)">
                            <i class="material-icons white-text">check</i>
                        </button>
                    </td>
                    <td>
                        <UptimeStatus :api='api'></UptimeStatus>
                        <SourceStatus :api='api'></SourceStatus>
                    </td>
                    </tr>
                    <tr v-if="total && total == 0">
                    <td colspan="4" class="center-align">
                        <h4>No Contributions Yet</h4><br>
                    </td>
                    </tr>
                </tbody>
                </table>
            </div>

            </div>
        </div>
    </div>

    <div class="blue-grey lighten-2 padding20 white-text center">
        <p>
            <i class="material-icons">error_outline</i> Did you know you can set a custom slug for your API's documentation? It's easy! Just click on any API on your dashboard and go to the <em>Settings</em> tab.<br />
            Use the <em>Custom Slug Registration Wizard</em> and get a custom URL for your API's documentation. E.g. <b>&lt;slug&gt;.smart-api.info</b>
        </p>
    </div>


    <VModal v-model="showModal" @confirm="confirm">
        <template v-slot:title>Settings</template>
        <div id="modal2" class="modal center-align">
        <div  class="modal-content" style="padding-top:45px;">
            <div class="row">
                <div class="col s12">
                <ul class="tabs transparent">
                    <li class="tab col s3"><a href="#test1" class="active blue-text">About</a></li>
                    <li class="tab col s3"><a class="blue-text" href="#test2">Slug Registration</a></li>
                    <li class="tab col s3"><a class="blue-text" href="#test3" @click="renderUserInteractions(apis[selectedAPIIndex].info.title)">User Interactions</a></li>
                </ul>
                </div>

                <div id="test1" class="col s12">
                <ul v-if="selectedAPIIndex || selectedAPIIndex === 0" class="collection with-header" style="border: none;">

                    <li class="collection-header padding20">
                    <Image img_width="100px"  alt="SmartAPI" img_name="logo-medium.svg" class="hide-on-small-only"></Image>
                    <h2 class="blue-text flow-text">
                        {{apis[selectedAPIIndex].info.title}}
                        <span class="versionBadge grey hide-on-small-only">Version {{apis[selectedAPIIndex].info.version}}</span>
                        <span v-if=" apis[selectedAPIIndex]?.openapi " class="versionBadge green hide-on-small-only">
                        OAS3
                        </span>
                        <span v-else-if=" apis[selectedAPIIndex]?.swagger " class="versionBadge blue hide-on-small-only">
                        Swagger2
                        </span>
                        <template class="show-on-small hide-on-med-and-up">
                        <span v-if=" apis[selectedAPIIndex]?.openapi " class="versionBadge green hide-on-med-and-up">
                            V3
                        </span>
                        <span v-else-if=" apis[selectedAPIIndex]?.swagger " class="versionBadge blue hide-on-med-and-up">
                            V2
                        </span>
                        </template>
                    </h2>
                    <hr />
                    <template v-if=" apis[selectedAPIIndex]?.swagger ">
                        <div class="yellow lighten-5 smallFont padding20">
                        APIs in Swagger V2 specification will experience limited functionality. <br />We recommend you update your metadata to OpenAPI V3 specification.
                        <br />
                        <a target="_blank" class="underlined" href="https://github.com/SmartAPI/smartAPI-Specification/blob/OpenAPI.next/versions/3.0.0.md">Learn More about OpenAPI V3 Specification <i class="fa fa-external-link-square" aria-hidden="true"></i></a>
                        <br />
                        <a href="/guide" class="green-text underlined">Use our guide to help you convert your API to OpenAPI V3 specification.</a>
                        </div>
                        <hr />
                    </template>
                    <div class="d-flex padding20" style="justify-content: center;">
                        <div class="blue-grey-text grey lighten-4 p-1"><small>API ID</small></div>
                        <div class='grey lighten-3 p-1 indigo-text'><small v-text="apis[selectedAPIIndex]._id"></small></div>
                    </div>
                    <a :href="'/ui/'+apis[selectedAPIIndex]._id" class="btn blue m-2">View API Documentation</a>
                    <a :href="'/registry?q='+apis[selectedAPIIndex]._id" class="btn indigo m-2">View API On SmartAPI Registry</a>
                    </li>
                    <template v-for='link in checkForAPIInfoLink(apis[selectedAPIIndex])' :key="link">
                    <li class="collection-item blue-grey lighten-4">
                        <a class="link blue-grey-text underlined" :href="link" target="_blank">
                        More Info
                        </a>
                    </li>
                    </template>
                    <li class="collection-item padding20 blue-grey lighten-5">
                    <p style="line-height: 1.2em;" class="blue-grey-text flow-text" v-html="compiledMarkdown(apis[selectedAPIIndex].info.description || '')"></p>
                    </li>
                    <li class="collection-item blue-grey lighten-5">
                    <i v-if="apis[selectedAPIIndex].info.termsOfService || apis[selectedAPIIndex].termsOfService" class="material-icons tiny blue-text">info_outline</i>
                    <a v-if="apis[selectedAPIIndex].info.termsOfService" :href="apis[selectedAPIIndex].info.termsOfService" target="_blank" class="blue-text">Terms of Service</a>
                    <a v-if="apis[selectedAPIIndex].termsOfService" :href="apis[selectedAPIIndex].termsOfService" target="_blank" class="blue-text">Terms of Service</a>

                    </li>
                    <li class="collection-item deep-orange lighten-2">
                    <h5>Danger Zone</h5>
                    <p>
                        Delete API metadata from SmartAPI registry permanently. This action cannot be undone.
                    </p>
                    <button type="button" @click="deleteForever(apis[selectedAPIIndex].info.title, apis[selectedAPIIndex]._id)" class="btn btn-small red white-text" 
                    data-tippy-content="<b class='red-text'>Delete Forever</b>">
                        Delete API
                    </button>
                    </li>
                </ul>
                </div>

                <div id="test2" class="col s12 white">
                <div v-if="selectedAPIIndex || selectedAPIIndex === 0" class="row">
                    <div class="col s12 m12 l12 center-align">
                    <h3 class="flow-text blue-grey-text padding20">Slug Registration Wizard</h3>
                    </div>
                    <div v-if='!hasShortName' class="col s12 m12 l12 center-align">
                    <Image class="hide-on-small-only" img_width="250px" img_name="wand.svg" alt='custom slug' style='border-radius: 10px;'></Image>
                    <p class="grey-text left-align">
                        Every project has a subdomain that is available to serve its documentation.<br />
                        By default we use your <i>API ID</i>. If you go to <span class="blue-text"><b>your-api-id</b>.smart-api.info</span> it should allow users to view your API documentation.
                    </p>
                    <p class="grey-text left-align">
                        You can also register a unique slug to make sharing your API easier.
                        <br />
                        If you go to <span class="blue-text"><b>your-slug</b>.smart-api.info</span>, it will take users to your API documentation.
                    </p>
                    <a v-if='!createOrEditMode' @click.prevent='createOrEditMode = !createOrEditMode' class="blue btn">Create a new slug</a>
                    <a v-if='createOrEditMode' @click.prevent='createOrEditMode = !createOrEditMode' class="red btn">Cancel</a>
                    </div>
                    <div v-if='hasShortName' class="col s12 m12 l12">
                    <p>
                        <i class="fa fa-check-circle-o green-text fa-5x" aria-hidden="true"></i>
                    </p>
                    <p class="grey-text">
                        You have registered your custom slug!
                        <br />
                        If you visit to link below, it will take users to your API documentation.
                    </p>
                    <div class="green-text flow-text">
                        <a :href=" 'http://'+apis[selectedAPIIndex]._meta.slug+'.smart-api.info'" target="_blank" class="green-text link">http://<b>{{apis[selectedAPIIndex]._meta.slug}}</b>.smart-api.info <i class="fa fa-external-link-square" aria-hidden="true"></i></a>
                        <br />
                        <hr />
                        <a class="btn green smallFont margin20" @click.prevent='createOrEditMode = !createOrEditMode'>Edit Slug</a>
                        <a v-if="hasShortName" class="btn red smallFont margin20" @click.prevent='deleteSlug'>Delete Slug</a>
                    </div>
                    </div>
                    <div v-if="createOrEditMode" style="width: 100%; display: flex; align-items: center;justify-content: center; flex-wrap: wrap;">
                    <div class="left-align padding20 grey-text" style="flex: 1; min-width: 100%;">
                        Slug length must be 4-50 characters (a-z) and/or numbers (0-9). Slugs will be converted to lower case. URL protected characters not allowed.
                    </div>
                    <div style="flex: 1; min-width: 200px;">
                        <input autocomplete="false" v-model='myShortName' placeholder="Enter your slug here" id="first_name" type="text" class="disabled browser-default margin20 grey lighten-5 blue-grey-text lighter" style="width: 85%; outline: none; padding: 10px; border-radius: 20px; border:var(--blue-medium) 2px solid;">
                    </div>
                    <div style="flex: 1; min-width: 200px;">
                        <p id="availabilityResults" v-bind:class="{'green-text': availableShortName, 'red-text': !availableShortName }">
                        <span v-if="myShortName" class="grey-text">http://</span>
                        <span v-if="myShortName">{{myShortName}}</span>
                        <span v-if="myShortName" class="grey-text">.smart-api.info</span>
                        <span v-if="!myShortName" class="grey-text">Check Slug Availability</span>
                        <i v-if='availableShortName && myShortName' class="fa fa-thumbs-up green-text" aria-hidden="true"></i>
                        <i v-if='!availableShortName && myShortName' class="fa fa-thumbs-down red-text" aria-hidden="true"></i>
                        <br />
                        <span v-if="myShortName.length < 3 && myShortName.length > 0" class="amber-text"><i class="tiny material-icons">warning</i> Too Short</span>
                        <span v-if="myShortName.length >50" class="orange-text"><i class="tiny material-icons">warning</i> Too Long</span><br v-if="myShortName.length <= 3 && invalidChars"/>
                        <span v-if="invalidChars" class="red-text"><i class="tiny material-icons">warning</i> Invalid Characters</span>
                        <span v-if="takenSlug" class="orange-text"><i class="tiny material-icons">warning</i> Taken Slug</span>
                        </p>
                    </div>
                    <div style="flex: 1; min-width: 200px;">
                        <a @click.prevent="setShortname" :disabled='!availableShortName && !hasShortName' :class="!availableShortName ? 'btn grey' : 'green btn pulse' " >Set Slug</a>
                    </div>

                    <div id="shortNameSuccess" class="center-align padding20 green smallFont" style="flex: 1; min-width: 100%; display: none;">
                        <h5 class="white-text"><i class="fa fa-check white-text" aria-hidden="true"></i> Slug Registered</h5>
                        <a href="#!" class="btn green modal-action modal-close">Close</a>
                    </div>
                    </div>
                </div>
                </div>

                <div id="test3" class="col s12 white">
                <div v-if="selectedAPIIndex || selectedAPIIndex === 0" class="row">
                    <div class="col s12 m12 l12 center-align">
                    <h3 class="flow-text blue-grey-text padding20">User Interactions</h3>
                    </div>
                    <div>
                    <h6 class="blue-text" v-text='apis[selectedAPIIndex].info.title'></h6>
                    <canvas id="myChart" width="400" height="400"></canvas>
                    <div>
                        <small>Views = Viewed API details, Documentation = Viewed API documentation, Searched = Searched API by name</small>
                    </div>
                    </div>
                </div>
                </div>
              </div>
            </div>
        </div>
    </VModal>

    </main>
</template>

<script>
import { mapGetters } from 'vuex'
import Chart from 'chart.js';
import moment from 'moment';
import {sortBy, get} from 'lodash'
import tippy from 'tippy.js';
import axios from 'axios'
import marked from 'marked'
import {Tabs} from 'materialize-css'

import UptimeStatus from '../components/UptimeStatus.vue';
import SourceStatus from '../components/SourceStatus.vue';

export default {
    name: "DashBoard",
    components:{
        UptimeStatus,
        SourceStatus
    },
    data: function(){
    return {
        confirmModal:{
            title:'',
            id:''
        },
        selectedAPI:{},
        inputApiName:'',
        apis:[
            {
"_id": "9c7027eec7ba101587f74e4b2ca2f7d2",
"_meta": {
"date_created": "2019-10-22T04:25:26.584170+00:00",
"last_updated": "2021-03-11T08:01:15.409916+00:00",
"url": "https://raw.githubusercontent.com/achave11/workflow-execution-service-schemas/wes_smartapi/openapi/workflow_execution_service.openapi.yaml",
"username": "achave11"
},
"_score": 1,
"_status": {
"refresh_status": 200,
"refresh_ts": "2021-03-11T08:01:15+00:00",
"uptime_status": "unknown",
"uptime_ts": "2021-03-11T08:07:21.638654"
},
"components": {
"schemas": {
"DefaultWorkflowEngineParameter": {
"description": "A message that allows one to describe default parameters for a workflow\nengine.",
"properties": {
"default_value": {
"description": "The stringified version of the default parameter. e.g. \"2.45\".",
"type": "string"
},
"type": {
"description": "Describes the type of the parameter, e.g. float.",
"type": "string"
}
},
"type": "object"
},
"ErrorResponse": {
"description": "An object that can optionally include information about the error.",
"properties": {
"msg": {
"description": "A detailed error message.",
"type": "string"
},
"status_code": {
"description": "The integer representing the HTTP status code (e.g. 200, 404).",
"type": "integer"
}
},
"type": "object"
},
"Log": {
"properties": {
"cmd": {
"items": {
"type": "string"
},
"title": "The command line that was run",
"type": "array"
},
"end_time": {
"title": "When the command completed",
"type": "string"
},
"exit_code": {
"format": "int32",
"title": "Exit code of the program",
"type": "integer"
},
"name": {
"title": "The task or workflow name",
"type": "string"
},
"start_time": {
"title": "When the command was executed",
"type": "string"
},
"stderr": {
"title": "Sample of stderr (not guaranteed to be entire log)",
"type": "string"
},
"stdout": {
"title": "Sample of stdout (not guaranteed to be entire log)",
"type": "string"
}
},
"title": "Log and other info",
"type": "object"
},
"ServiceInfo": {
"description": "A message containing useful information about the running service, including supported versions and\ndefault settings.",
"properties": {
"auth_instructions_url": {
"description": "A URL that will help a in generating the tokens necessary to run a workflow using this\nservice.",
"type": "string"
},
"default_workflow_engine_parameters": {
"description": "Each workflow engine can present additional parameters that can be sent to the\nworkflow engine. This message will list the default values, and their types for each\nworkflow engine.",
"items": {
"$ref": "#/components/schemas/DefaultWorkflowEngineParameter"
},
"type": "array"
},
"supported_filesystem_protocols": {
"description": "The filesystem protocols supported by this service, currently these may include common\nprotocols such as 'http', 'https', 'sftp', 's3', 'gs', 'file', 'synapse', or others as\nsupported by this service.",
"items": {
"type": "string"
},
"type": "array"
},
"supported_wes_versions": {
"items": {
"type": "string"
},
"title": "The version(s) of the WES schema supported by this service",
"type": "array"
},
"system_state_counts": {
"additionalProperties": {
"format": "int64",
"type": "integer"
},
"description": "The system statistics, key is the statistic, value is the count of workflows in that state.\nSee the State enum for the possible keys.",
"type": "object"
},
"tags": {
"additionalProperties": {
"type": "string"
},
"title": "A key-value map of arbitrary, extended metadata outside the scope of the above but useful\nto report back",
"type": "object"
},
"workflow_engine_versions": {
"additionalProperties": {
"type": "string"
},
"title": "The engine(s) used by this WES service, key is engine name e.g. Cromwell and value is version",
"type": "object"
},
"workflow_type_versions": {
"additionalProperties": {
"$ref": "#/components/schemas/WorkflowTypeVersion"
},
"title": "A map with keys as the workflow format type name (currently only CWL and WDL are used\nalthough a service may support others) and value is a workflow_type_version object which\nsimply contains an array of one or more version strings",
"type": "object"
}
},
"type": "object"
},
"State": {
"default": "UNKNOWN",
"description": "- UNKNOWN: The state of the task is unknown.\n\nThis provides a safe default for messages where this field is missing,\nfor example, so that a missing field does not accidentally imply that\nthe state is QUEUED.\n - QUEUED: The task is queued.\n - INITIALIZING: The task has been assigned to a worker and is currently preparing to run.\nFor example, the worker may be turning on, downloading input files, etc.\n - RUNNING: The task is running. Input files are downloaded and the first Executor\nhas been started.\n - PAUSED: The task is paused.\n\nAn implementation may have the ability to pause a task, but this is not required.\n - COMPLETE: The task has completed running. Executors have exited without error\nand output files have been successfully uploaded.\n - EXECUTOR_ERROR: The task encountered an error in one of the Executor processes. Generally,\nthis means that an Executor exited with a non-zero exit code.\n - SYSTEM_ERROR: The task was stopped due to a system error, but not from an Executor,\nfor example an upload failed due to network issues, the worker's ran out\nof disk space, etc.\n - CANCELED: The task was canceled by the user.",
"enum": [
"UNKNOWN",
"QUEUED",
"INITIALIZING",
"RUNNING",
"PAUSED",
"COMPLETE",
"EXECUTOR_ERROR",
"SYSTEM_ERROR",
"CANCELED"
],
"title": "Enumeration of states for a given workflow request",
"type": "string"
},
"WesObject": {
"additionalProperties": true,
"description": "An arbitrary structured object.",
"type": "object"
},
"WorkflowDescription": {
"properties": {
"state": {
"$ref": "#/components/schemas/State",
"title": "REQUIRED"
},
"workflow_id": {
"title": "REQUIRED",
"type": "string"
}
},
"title": "Small description of workflows, returned by server during listing",
"type": "object"
},
"WorkflowListResponse": {
"description": "The service will return a workflow_list_response when receiving a successful workflow_list_request.",
"properties": {
"next_page_token": {
"description": "A token, which when provided in a workflow_list_request, allows one to retrieve the next page\nof results.",
"type": "string"
},
"workflows": {
"description": "A list of workflows that the service has executed or is executing.",
"items": {
"$ref": "#/components/schemas/WorkflowDescription"
},
"type": "array"
}
},
"type": "object"
},
"WorkflowLog": {
"properties": {
"outputs": {
"$ref": "#/components/schemas/WesObject",
"title": "the outputs"
},
"request": {
"$ref": "#/components/schemas/WorkflowRequest",
"description": "The original request message used to initiate this execution."
},
"state": {
"$ref": "#/components/schemas/State",
"title": "state"
},
"task_logs": {
"items": {
"$ref": "#/components/schemas/Log"
},
"title": "the logs, and other key info like timing and exit code, for each step in the workflow",
"type": "array"
},
"workflow_id": {
"title": "workflow ID",
"type": "string"
},
"workflow_log": {
"$ref": "#/components/schemas/Log",
"title": "the logs, and other key info like timing and exit code, for the overall run of this workflow"
}
},
"type": "object"
},
"WorkflowRequest": {
"description": "To execute a workflow, send a workflow request including all the details needed to begin downloading\nand executing a given workflow.",
"properties": {
"tags": {
"additionalProperties": {
"type": "string"
},
"title": "OPTIONAL\nA key-value map of arbitrary metadata outside the scope of the workflow_params but useful to track with this workflow request",
"type": "object"
},
"workflow_descriptor": {
"description": "OPTIONAL\nThe workflow CWL or WDL document, must provide either this or workflow_url. By combining\nthis message with a workflow_type_version offered in ServiceInfo, one can initialize\nCWL, WDL, or a base64 encoded gzip of the required workflow descriptors. When files must be\ncreated in this way, the `workflow_url` should be set to the path of the main\nworkflow descriptor.",
"type": "string"
},
"workflow_engine_parameters": {
"additionalProperties": {
"type": "string"
},
"description": "OPTIONAL\nAdditional parameters can be sent to the workflow engine using this field. Default values\nfor these parameters are provided at the ServiceInfo endpoint.",
"type": "object"
},
"workflow_params": {
"$ref": "#/components/schemas/WesObject",
"description": "REQUIRED\nThe workflow parameterization document (typically a JSON file), includes all parameterizations for the workflow\nincluding input and output file locations."
},
"workflow_type": {
"title": "REQUIRED\nThe workflow descriptor type, must be \"CWL\" or \"WDL\" currently (or another alternative supported by this WES instance)",
"type": "string"
},
"workflow_type_version": {
"title": "REQUIRED\nThe workflow descriptor type version, must be one supported by this WES instance",
"type": "string"
},
"workflow_url": {
"description": "OPTIONAL\nThe workflow CWL or WDL document, must provide either this or workflow_descriptor. When a base64 encoded gzip of\nworkflow descriptor files is offered, the `workflow_url` should be set to the relative path\nof the main workflow descriptor.",
"type": "string"
}
},
"type": "object"
},
"WorkflowRunId": {
"properties": {
"workflow_id": {
"title": "workflow ID",
"type": "string"
}
},
"type": "object"
},
"WorkflowStatus": {
"properties": {
"state": {
"$ref": "#/components/schemas/State",
"title": "state"
},
"workflow_id": {
"title": "workflow ID",
"type": "string"
}
},
"type": "object"
},
"WorkflowTypeVersion": {
"description": "Available workflow types supported by a given instance of the service.",
"properties": {
"workflow_type_version": {
"description": "an array of one or more acceptable types for the Workflow Type. For\nexample, to send a base64 encoded WDL gzip, one could would offer\n\"base64_wdl1.0_gzip\". By setting this value, and the path of the main WDL\nto be executed in the workflow_url to \"main.wdl\" in the WorkflowRequest.",
"items": {
"type": "string"
},
"type": "array"
}
},
"type": "object"
}
}
},
"info": {
"contact": {
"email": "davidcs@ucsc.edu",
"name": "David Steinberg"
},
"description": "A minimal common API which allows users to make workflow requests programmatically, adding the ability to scale up.",
"termsOfService": "https://www.ga4gh.org/policies/termsandconditions.html",
"title": "Sandbox Workflow Execution Service",
"version": "0.2.1",
"x-implementationLanguage": "en"
},
"openapi": "3.0.0",
"paths": {
"/service-info": {
"get": {
"operationId": "GetServiceInfo",
"responses": {
"200": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/ServiceInfo"
}
}
},
"description": ""
},
"400": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/ErrorResponse"
}
}
},
"description": "The request is malformed."
},
"401": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/ErrorResponse"
}
}
},
"description": "The request is unauthorized."
},
"403": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/ErrorResponse"
}
}
},
"description": "The requester is not authorized to perform this action."
},
"500": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/ErrorResponse"
}
}
},
"description": "An unexpected error occurred."
}
},
"summary": "Get information about Workflow Execution Service.  May include information related (but\nnot limited to) the workflow descriptor formats, versions supported, the WES API versions supported, and information about general the service availability.",
"tags": [
"WorkflowExecutionService"
],
"x-swagger-router-controller": "ga4gh.wes.server"
}
},
"/workflows": {
"get": {
"operationId": "ListWorkflows",
"parameters": [
{
"description": "OPTIONAL\nNumber of workflows to return in a page.",
"in": "query",
"name": "page_size",
"required": false,
"schema": {
"format": "int64",
"type": "integer"
}
},
{
"description": "OPTIONAL\nToken to use to indicate where to start getting results. If unspecified, returns the first\npage of results.",
"in": "query",
"name": "page_token",
"required": false,
"schema": {
"type": "string"
}
},
{
"description": "OPTIONAL\nFor each key, if the key's value is empty string then match workflows that are tagged with\nthis key regardless of value.",
"in": "query",
"name": "tag_search",
"required": false,
"schema": {
"type": "string"
}
}
],
"responses": {
"200": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/WorkflowListResponse"
}
}
},
"description": ""
},
"400": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/ErrorResponse"
}
}
},
"description": "The request is malformed."
},
"401": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/ErrorResponse"
}
}
},
"description": "The request is unauthorized."
},
"403": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/ErrorResponse"
}
}
},
"description": "The requester is not authorized to perform this action."
},
"500": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/ErrorResponse"
}
}
},
"description": "An unexpected error occurred."
}
},
"summary": "List the workflows, this endpoint will list the workflows in order of oldest to newest.\nThere is no guarantee of live updates as the user traverses the pages, the behavior should be\ndecided (and documented) by each implementation.\nTo monitor a given execution, use GetWorkflowStatus or GetWorkflowLog.",
"tags": [
"WorkflowExecutionService"
],
"x-swagger-router-controller": "ga4gh.wes.server"
},
"post": {
"operationId": "RunWorkflow",
"requestBody": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/WorkflowRequest"
}
}
},
"required": true
},
"responses": {
"200": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/WorkflowRunId"
}
}
},
"description": ""
},
"400": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/ErrorResponse"
}
}
},
"description": "The request is malformed."
},
"401": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/ErrorResponse"
}
}
},
"description": "The request is unauthorized."
},
"403": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/ErrorResponse"
}
}
},
"description": "The requester is not authorized to perform this action."
},
"500": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/ErrorResponse"
}
}
},
"description": "An unexpected error occurred."
}
},
"summary": "Run a workflow, this endpoint will allow you to create a new workflow request and\nretrieve its tracking ID to monitor its progress.  An important assumption in this\nendpoint is that the workflow_params JSON will include parameterizations along with\ninput and output files.  The latter two may be on S3, Google object storage, local filesystems,\netc.  This specification makes no distinction.  However, it is assumed that the submitter\nis using URLs that this system both understands and can access. For Amazon S3, this could\nbe accomplished by given the credentials associated with a WES service access to a\nparticular bucket.  The details are important for a production system and user on-boarding\nbut outside the scope of this spec.",
"tags": [
"WorkflowExecutionService"
],
"x-swagger-router-controller": "ga4gh.wes.server"
}
},
"/workflows/{workflow_id}": {
"delete": {
"operationId": "CancelJob",
"parameters": [
{
"in": "path",
"name": "workflow_id",
"required": true,
"schema": {
"type": "string"
}
}
],
"responses": {
"200": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/WorkflowRunId"
}
}
},
"description": ""
},
"401": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/ErrorResponse"
}
}
},
"description": "The request is unauthorized."
},
"403": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/ErrorResponse"
}
}
},
"description": "The requester is not authorized to perform this action."
},
"404": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/ErrorResponse"
}
}
},
"description": "The requested Workflow wasn't found."
},
"500": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/ErrorResponse"
}
}
},
"description": "An unexpected error occurred."
}
},
"summary": "Cancel a running workflow.",
"tags": [
"WorkflowExecutionService"
],
"x-swagger-router-controller": "ga4gh.wes.server"
},
"get": {
"operationId": "GetWorkflowLog",
"parameters": [
{
"in": "path",
"name": "workflow_id",
"required": true,
"schema": {
"type": "string"
}
}
],
"responses": {
"200": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/WorkflowLog"
}
}
},
"description": ""
},
"401": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/ErrorResponse"
}
}
},
"description": "The request is unauthorized."
},
"403": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/ErrorResponse"
}
}
},
"description": "The requester is not authorized to perform this action."
},
"404": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/ErrorResponse"
}
}
},
"description": "The requested Workflow found."
},
"500": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/ErrorResponse"
}
}
},
"description": "An unexpected error occurred."
}
},
"summary": "Get detailed info about a running workflow.",
"tags": [
"WorkflowExecutionService"
],
"x-swagger-router-controller": "ga4gh.wes.server"
}
},
"/workflows/{workflow_id}/status": {
"get": {
"operationId": "GetWorkflowStatus",
"parameters": [
{
"in": "path",
"name": "workflow_id",
"required": true,
"schema": {
"type": "string"
}
}
],
"responses": {
"200": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/WorkflowStatus"
}
}
},
"description": ""
},
"401": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/ErrorResponse"
}
}
},
"description": "The request is unauthorized."
},
"403": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/ErrorResponse"
}
}
},
"description": "The requester is not authorized to perform this action."
},
"404": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/ErrorResponse"
}
}
},
"description": "The requested Workflow wasn't found."
},
"500": {
"content": {
"application/json": {
"schema": {
"$ref": "#/components/schemas/ErrorResponse"
}
}
},
"description": "An unexpected error occurred."
}
},
"summary": "Get quick status info about a running workflow.",
"tags": [
"WorkflowExecutionService"
],
"x-swagger-router-controller": "ga4gh.wes.server"
}
}
},
"servers": [
{
"url": "http://wes.ucsc-cgp-dev.org:8080/ga4gh/wes/v1"
}
],
"tags": [
{
"description": "A shared virtual space where scientists can work with the digital objects of biomedical research such as data and analytical tools.",
"name": "NIHdatacommons"
}
]
}
        ],
        total: 0,
        confirmDelete: true,
        searchQuery:'',
        searchResults:[],
        myShortName:'',
        availableShortName: false,
        hasShortName: false,
        createOrEditMode: false,
        invalidChars: false,
        takenSlug: false,
        selectedAPIIndex:'',
        loading: false,
        // analytics
        analytics: Object,
        tags: Array,
        showModal: false
        }
    },
    computed:{
        results: function(){
        return this.searchResults.length ? this.searchResults : this.apis;
        },
        ...mapGetters([
            'loggedIn',
            'userInfo'
        ])
    },
    methods:{
        confirm() {
          this.showModal = false
        },
        renderUserInteractions(name){
            let self = this;
            let data = self.getHitsFor(name);
            var ctx = document.getElementById('myChart');

            new Chart(ctx, {
                'type': 'bar',
                'data': data,
                'options': {
                'legend': { display: false },
                'title': {
                    display: true,
                    text: 'User Interactions (Last 30 days)'
                },
                'scales': {
                    yAxes: [{
                        ticks: {
                            precision:0
                        }
                    }],
                },
                }
            });
        },
        validate(url){
        let self = this;
        if (url) {
            var bodyFormData = new FormData();
            bodyFormData.append('url', url);
            axios({
                method: "post",
                url: '/api/validate',
                data: bodyFormData,
                headers: { "Content-Type": "multipart/form-data" },
            }).then(res=>{
            self.$swal({
                imageUrl: '/static/img/api-sucess.svg',
                imageWidth: 300,
                title: 'Great! Everything looks good!',
                footer: "<h5 class='green-text'>" + res.data.details + "</h5>"
                })
            }).catch(err=>{
            if(err?.response?.data){
            // console.log('[Error]:', err.response)
            if(err?.response?.data?.error && err.response.data.error == "Conflict"){
            self.$swal({
                title: "Wait a second...",
                html:'<h3>Looks like this API already exists</h3><p>If you are the owner of this API you can refresh it via the <a href="/dashboard">user dashboard</a></p>',
                imageUrl: '/static/img/api-overwrite.svg',
                imageWidth: 300,
                confirmButtonText: 'OK',
            });
            }
            else if(err.response.data?.details && err.response.data.details == "API exists"){
            self.$swal({
                title: "Wait a second...",
                html:'<h3>Looks like this API already exists</h3><p>If you are the owner of this API you can refresh it via the <a href="/dashboard">user dashboard</a></p>',
                imageUrl: '/static/img/api-fail.svg',
                imageWidth: 300,
                confirmButtonText: 'OK',
            });
            }
            else if(err.response.data?.details && err.response.data.details.includes("Validation Error")){
            self.$swal({
                title: "Oh no, there's a problem!",
                imageUrl: '/static/img/api-fail.svg',
                imageWidth: 300,
                confirmButtonText: 'OK',
                html:`<h5>Here's what we found:</h5>
                    <div class="padding20 orange lighten-5 codeBox"><code>`+err.response.data.details || err.response.data+`</code></div>`,
                footer:`<p><b class="red-text">Need help?</b> Take a look at OpenAPI specification examples <a href="https://github.com/NCATSTranslator/translator_extensions" target="_blank" rel="nonreferrer">here</a>.</p>`
            })
            }
            else{
            self.$swal({
                title: "Oops, there's an issue!",
                imageUrl: '/static/img/api-fail.svg',
                imageWidth: 300,
                confirmButtonText: 'OK',
                html:`<h5>Here's what we found:</h5>
                    <div class="padding20 orange lighten-5 codeBox"><code>`+err.response.data.details || err.response.data+`</code></div>`,
                footer:`<p><b class="red-text">Need help?</b> Learn more about and look at examples of SmartAPI extensions <a href="https://github.com/NCATSTranslator/translator_extensions" target="_blank" rel="nonreferrer">here</a>.</p>`
            })
            }
            }
            });
        } else {
            self.$swal.fire({type:'error',
            toast:true,
            title: 'Missing URL',
            showConfirmButton:false,
            timer:1000})
        }
        },
        getApis: function(){
        var self=this;

        self.apis=[];
        let url = "/api/query?size=100&q=_meta.username:"+self.userInfo.login

        axios.get(`${url}&timestamp=${new Date().getTime()}`).then(function(response){
                self.apis = sortBy(response.data.hits,'info.title');
                self.total = response.data.total;
                self.hideLoading();

            }).catch(err=>{
            const toast = self.$swal.mixin({
                toast: true,
                position: 'top',
                showConfirmButton: false,
                timer: 2000
            });
            self.hideLoading();

            toast({
                type: 'error',
                title: 'Failed to load APIS'
            })
            throw err;
            });

        },
        compiledMarkdown: function (mdtext) {
            return marked(mdtext)
        },
        deleteForever: function(title, apiID){
        // ID for api to be deleted forever
        var self = this;
        self.showLoading();
        axios.delete('/api/metadata/'+apiID).then(response=>{
            //sucessful deletion
            self.hideLoading();
            if( response.data.success ){
            window.location.reload()
            }else if( !response.data.success ){
            const toast = self.$swal.mixin({
                toast: true,
                position: 'top',
                showConfirmButton: false,
                timer: 2000
            });

            toast({
                type: 'error',
                title: 'Failed to delete '+title
            })
            }
        }).catch(error=>{
            //error deleting
            throw(error);
        });
        self.getApis();

        },
        showMessage(title, status){
        const toast = self.$swal.mixin({
                toast: true,
                position: 'top',
                showConfirmButton: false,
                timer: 4000
            });
        switch (status) {
            case 'updated':
            self.$swal({
                title: "Sweet!",
                confirmButtonText: 'OK',
                imageUrl: '/static/img/api-sucess.svg',
                imageWidth: 200,
                html: "<h5><b>"+title+"</b> was updated!</h5>",
                footer: "<p>You may look at your latest changes on our <a href='/registry?q="+title+"'>API registry</a>.</p>"
            })
            break;

            case 'not_modified':
            self.$swal({
                title: "Hmmm...",
                imageUrl: '/static/img/api-thinking.svg',
                imageWidth: 200,
                confirmButtonText: 'OK',
                html: "<h5><b>"+title+"</b> has no changes.</h5>",
                footer: "<p>If this doesn't sound right, wait a few minutes and try again. Repositories such as GitHub may have a delay updating their raw data.</p>"
            })
            break;

            case 'invalid':
            self.$swal({
                title: "Oops!",
                confirmButtonText: 'OK',
                imageUrl: '/static/img/api-fail.svg',
                imageWidth: 200,
                html: "<h5 class='red-text'>New version found but there's validation errors.</h5>",
                footer: "<p>Click on <b class='indigo-text'>Validate Only</b> to see validation results. Once they are resolved you can <b class='green-text'>Refresh</b> and synchronize your metadata to its latest version.</p>"
            })
            break;

            case 'nofile':
            self.$swal({
                title: "Oh no!",
                confirmButtonText: 'OK',
                imageUrl: '/static/img/api-error.svg',
                imageWidth: 200,
                html: "<h6 class='red-text'>Looks like the source file no longers exists or is not reachable</h6>",
                footer: "<p>This issue can only be resolved by restoring your source file or deleting this API and re-registering as a new API with a working source file.</p>"
            })
            break;
        
            default:
            toast({
                title: 'NAME: <b>' + title + '</b> - STATUS: ' + status
                })
            break;
        }
        },
        refreshThis: function(title, id){
        var self = this;
        self.showLoading();
        axios.put('/api/metadata/'+id).then(res=>{
            if( res.data.success ){
            self.showMessage(title, res.data.status)
            self.hideLoading();
            }else if( !res.data.success ){
            self.showMessage(title, res.data.status)
            self.hideLoading();
            }
        }).catch(err=>{
            if (err?.response?.data?.status) {
            self.showMessage(title, err.response.data.status)
            } else {
            const toast = self.$swal.mixin({
                toast: true,
                position: 'top',
                showConfirmButton: false,
                timer: 4000
            });
            toast({
                type: 'error',
                title: title+' failed to refresh'
            })
            }
            self.hideLoading();
            throw(err);
        });
        self.getApis();
        },
        showLoading: function(){
        this.loading = true;
        },
        hideLoading: function(){
        this.loading = false;
        },
        getDetails: function(index){
        var elems = document.querySelectorAll('.tabs');
        Tabs.init(elems);

        var self = this;
        self.showModal = true;
        //modal will show the apis index of the item clicked
        self.selectedAPIIndex = index;
        //hasShortName sets display for slug registration view
        if (self.apis[index]._meta.slug) {
            self.hasShortName=true;
        }else{
            self.hasShortName=false;
        }
        },
        checkForAPIInfoLink: function(api){
        // console.log(api);
        if (get(api, 'info.contact.x-id')) {
            return [api.info.contact['x-id']];
        }
        else if (get(api, 'info.contact.url')) {
            return [api.info.contact.url];
        }
        else{
            return ['http://smart-api.info/'];
        }
        },
        convertDate: function(timestamp){
        var date = new Date(timestamp);
        date = moment(date).format('LLL');
        return date;
        },
        reloadAPIs: function(){
        this.showLoading();
        this.getUserInfo();
        },
        evaluateShortname: function(){
        var self = this;
        axios.get(`/api/query?q=__all__&filters={"_meta.slug":["`+this.myShortName+`"]}&fields=_meta`).then(response=>{
            //console.log(response.data.hits);
            if (response.data.total.value) {
            self.availableShortName = false;
            self.takenSlug = true;
            return false;
            }else{
            self.availableShortName = true;
            self.takenSlug = false;
            return true;
            }
        }).catch(error =>{
            self.availableShortName = false;
            throw error;
        })

        },
        setShortname: function(){
        //claim it button clicked
        var self = this;
        self.loading = false;
        axios.put('/api/metadata/'+self.apis[self.selectedAPIIndex]._id+'?slug='+self.myShortName).then(response=>{
            if( response.data.success ){
            self.apis[self.selectedAPIIndex]._meta.slug= response.data[self.apis[self.selectedAPIIndex]._id+'._meta.slug'];
            self.myShortName = '';

            const toast = self.$swal.mixin({
                toast: true,
                position: 'top',
                showConfirmButton: false,
                timer: 2000
            });

            toast({
                type: 'success',
                title:'Slug was registered'
            })

            self.createOrEditMode = false;
            self.hasShortName = true;
            self.loading = true;
            }else if( !response.data.success ){
            self.loading = false;
            const toast = self.$swal.mixin({
                toast: true,
                position: 'top',
                showConfirmButton: false,
                timer: 2000
            });

            toast({
                type: 'error',
                title:response.data.error
            })
            }
        }).catch(error=>{
            throw error;
        });
        },
        deleteSlug: function(){
        //delete it button clicked
        var self = this;
        self.loading = false;
        axios.delete('/api/metadata/'+self.apis[self.selectedAPIIndex]._id+"?slug="+self.apis[self.selectedAPIIndex]._meta.slug).then(response=>{
            if( response.data.success ){
            self.apis[self.selectedAPIIndex]._meta.slug= '';
            const toast = self.$swal.mixin({
                toast: true,
                position: 'top',
                showConfirmButton: false,
                timer: 2000
            });

            toast({
                type: 'success',
                title:'Slug was deleted'
            })
            self.createOrEditMode = false;
            self.hasShortName = false;
            self.loading = true;
            }else if( !response.data.success ){
            self.loading = false;
            const toast = self.$swal.mixin({
                toast: true,
                position: 'top',
                showConfirmButton: false,
                timer: 2000
            });

            toast({
                type: 'error',
                title:'Slug could not be set'
            })
            }
        }).catch(error=>{
            throw error;
        });
        },
        getAnalytics(){
        var self = this;
        axios.get('	https://gasuperproxy-1470690417190.appspot.com/query?id=ahxzfmdhc3VwZXJwcm94eS0xNDcwNjkwNDE3MTkwchULEghBcGlRdWVyeRiAgIDMgsmRCgw').then(res=>{
            if (res.data.rows) {
            self.analytics = res.data.rows;
            }
        }).catch(err=>{
            throw err;
        });
        },
        getHitsFor(apiname){
        var self = this;
        let data={'labels':[],'datasets':[]};
        let label = '';
        let dataArray=[];

        for (var i = 0; i < self.analytics.length; i++) {
            if (self.analytics[i][1].toLowerCase() === apiname.toLowerCase()) {
            label = self.analytics[i][0].toUpperCase();
            if (label == "EXPANDED") {
                label = "VIEWS"
            }
            data.labels.push(label);
            let number = self.analytics[i][2];
            dataArray.push(number)
            }
        }
        data.datasets.push({'label':"Users",'data':dataArray,'backgroundColor': ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],})
        return data
        },
    },
    mounted: function(){
        let self = this;
        self.showLoading();
        self.getAnalytics();
        // self.getApis();

        /*eslint-disable */
        tippy('.tipped',{
            placement: 'top',
            theme:'light',
            interactive:true,
            animation: false,
            allowHTML: true,
            onShow(instance) {
                let msg = instance.reference.dataset.tippyInfo;
                instance.setContent("<div class='p-1 blue-text'>"+msg+"</div>")
            },
        });
        /*eslint-enable */

    },
    watch: {
        inputApiName: function (input) {
        if(input.trim() === this.confirmModal.title){
            this.confirmDelete = false;
        }
        else{
            this.confirmDelete = true;
        }
        },
        searchQuery: function(query){
        if(!query){
            this.searchResults = [];
        }else{
            let result = this.apis.filter(o => o.info.title.toLowerCase().includes(query.toLowerCase()));
            this.searchResults = result;
        }
        },
        myShortName: function(shortname){
        var self = this;
        self.myShortName = self.myShortName.toLowerCase();
        /*eslint-disable */
        var re = /[^a-zA-Z0-9\-\_\~]/;
        /*eslint-enable */
        self.invalidChars = false;
        if (re.test(self.myShortName) ) {
            self.invalidChars = true;
        }
        if( !re.test(self.myShortName) && shortname.length >= 3 && shortname.length <= 50 ) {
            self.takenSlug = false;
            self.evaluateShortname();
        }else if(re.test(self.myShortName) && shortname.length >= 3 && shortname.length <= 50){
            self.invalidChars = true;
            self.availableShortName = false;
        }else{
            self.availableShortName = false;
        }
        }
    }
}
</script>

<style lang='css'>
    .pillStatus{
    display: flex;
    justify-content: space-evenly;
    align-items: stretch;
    margin: 5px;
    }
    .pillStatus div{
    flex-grow: 1;
    flex-basis: 50%;
    align-content: center;
    padding: 3px 6px;
    text-align: center;
    font-size: .8em !important;
    color: #434849;
    }
    .pillStatus div:first-child{
    border-top-left-radius: 5px;
    border-bottom-left-radius: 5px;
    }
    .pillStatus div:last-child{
    border-top-right-radius: 5px;
    border-bottom-right-radius: 5px;
    }
    .m-2{
    margin: 1rem;
    }
    .dashboard-header{
        display: flex;
        justify-content: space-evenly;
        flex-wrap: wrap;
        align-items: center;
    }
    .dash-photo{
        box-shadow: 5px 5px 5px #273238;
        border: white 2px solid;
    }
</style>