<template>
  <main id="dashApp" style="min-height:90vh;" class="grey lighten-2" v-cloak>
    <MetaHead title="SmartAPI | My Dashboard"></MetaHead>
    <!-- IF NO USER INFO DISPLAY LOGIN-->
    <div v-if="!loggedIn" class="padding20 card-panel white d-flex justify-content-center align-items-center" style="min-height:80vh;">
        <div class="center-align">
            <h5>
                <Image img_name="api-stop.svg" img_width="250px"></Image>
            </h5>
            <h5 class="text_h3 blue-grey-text-text">
            You Must Be Logged In To Use Your Dashboard
            </h5>
            <a href="/oauth" class="btn green">
            Login
            </a>
        </div>
    </div>
    <!-- LOADING -->
    <div v-if="loading" id="loading-overlay" class="center-align">
        <div class="center-align">
            <div class="lds-ellipsis"><div></div><div></div><div></div><div></div></div>
        </div>
    </div>
    <!-- Loading END -->
    <!-- IF USER INFO DISPLAY DASHBOARD -->
    <div v-if="loggedIn" class="row" style="margin-bottom: 0; width: 100%;min-height:70vh;">
        <div class="col s12 padding20">
            <div class="dashboard-header">
                <div class="grey-text dashHead">
                    <template v-if="userInfo && userInfo.avatar_url">
                        <img width="80" 
                            height="80" 
                            :src="userInfo.avatar_url" 
                            class="responsive-img circle dash-photo"
                            :alt="userInfo.login">
                    </template>
                    <Image v-else
                        id="dashboardPhoto" 
                        img_width="80px" 
                        img_height="80px" 
                        img_name="user-default.png" 
                        class="responsive-img circle dash-photo" 
                        :alt="userInfo.login"></Image>
                    <h5 v-if="userInfo?.name" style="margin-left:10px;">
                        <b>
                            Hello, <a target="_blank" :href="'https://github.com/'+userInfo.login">{{ userInfo?.name.split(" ")[0] || userInfo.login }}</a>!
                        </b>
                    </h5>
                </div>
            </div>
        </div>
        <div class="col s12 center-align">
            <div class="container row" style="margin:auto;">
            <div class="p-1 col s12">
                <input v-model='searchQuery' placeholder="Search by API name" type="text" class="browser-default margin20 grey darken-1 l-blue-text lighter" style="width: 40%; outline: none; padding: 10px; border-radius: 20px; border:var(--blue-light) 2px solid;"/>
            </div>

            <div class="col s12 card-panel">
                <table class="striped highlight responsive-table">
                <thead>
                    <tr style="font-weight: 100; color: #d3d3d3; font-size:12px;">
                        <th>Name ({{total}})</th>
                        <th>Last Updated</th>
                        <th>Refresh</th>
                        <th>Validate</th>
                        <th>Uptime Check</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(api,index) in results" :key="api.info.title+index">
                    <td>
                        <h6 class="left-align">
                        <b>{{ api.info.title }}</b>&nbsp;
                        <small>
                            <span class="grey-text">V {{api.info.version}}</span>
                        </small>&nbsp;
                        <small v-if="api?.openapi" class="green-text">
                            OAS3
                        </small>&nbsp;
                        <small v-else-if="api?.swagger" class="blue-text">
                            Swagger2
                        </small>&nbsp;
                        <button class="smallButton" @click="getDetails(api)">
                            settings
                        </button>
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
                        <button type="button" @click="checkUptime(api._id)" class="btn btn-small scale-in-center deep-purple white-text tipped"
                            data-tippy-info="<b class='indigo-text'>Check current uptime status">
                            <i class="material-icons white-text">poll</i>
                        </button>
                    </td>
                    <td class="right-align">
                        <UptimeStatus :style="{marginBottom:'10px'}" :uptime_status='api?._status?.uptime_status' :err_msg="api?._status?.uptime_msg"></UptimeStatus>
                        <SourceStatus :refresh_status='api?._status?.refresh_status'></SourceStatus>
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

    <div class="blue-grey darken-2 padding20 white-text center">
        <p>
            <i class="material-icons">error_outline</i> Did you know you can set a custom slug for your API's documentation? It's easy! Just click on any API on your dashboard and go to the <em>Settings</em> tab.<br />
            Use the <em>Custom Slug Registration Wizard</em> and get a custom URL for your API's documentation. E.g. <b>&lt;slug&gt;.smart-api.info</b>
        </p>
    </div>


    <VModal v-model="showModal" @confirm="showModal = false">
        <template v-slot:title>Settings</template>
        <div class="center-align">
            <div v-if="selectedAPI && selectedAPI?.info?.title" style="padding-top:45px;">
            <div class="row">
                <div class="col s12">
                <ul class="tabs transparent">
                    <li class="tab col s3"  @click="tabSelected = 1"><a href="javascript:void(0);" class="active blue-text">API Metadata</a></li>
                    <li class="tab col s3"  @click="tabSelected = 2"><a class="blue-text" href="javascript:void(0);">Slug Registration</a></li>
                    <li class="tab col s3"  @click="tabSelected = 3"><a class="blue-text" href="javascript:void(0);">User Interactions</a></li>
                    <li class="tab col s3"  @click="tabSelected = 4"><a class="blue-text" href="javascript:void(0);">Delete</a></li>
                </ul>
                </div>

                <div v-show="tabSelected == 1" id="test1" class="col s12">
                <ul class="collection with-header" style="border: none;">

                    <li class="collection-header padding20">
                    <Image img_width="100px"  alt="SmartAPI" img_name="api-editor.svg" class="hide-on-small-only"></Image>
                    <h2 class="blue-text flow-text">
                        {{selectedAPI.info.title}}
                        <span class="versionBadge grey hide-on-small-only">Version {{selectedAPI.info.version}}</span>
                        <span v-if=" selectedAPI?.openapi " class="versionBadge green hide-on-small-only">
                        OAS3
                        </span>
                        <span v-else-if=" selectedAPI?.swagger " class="versionBadge blue hide-on-small-only">
                        Swagger2
                        </span>
                        <template class="show-on-small hide-on-med-and-up">
                        <span v-if=" selectedAPI?.openapi " class="versionBadge green hide-on-med-and-up">
                            V3
                        </span>
                        <span v-else-if=" selectedAPI?.swagger " class="versionBadge blue hide-on-med-and-up">
                            V2
                        </span>
                        </template>
                    </h2>
                    <hr />
                    <template v-if=" selectedAPI?.swagger ">
                        <div class="yellow lighten-5 smallFont padding20">
                        APIs in Swagger V2 specification will experience limited functionality. <br />We recommend you update your metadata to OpenAPI V3 specification.
                        <br />
                        <a target="_blank" class="underlined" href="https://github.com/SmartAPI/smartAPI-Specification/blob/OpenAPI.next/versions/3.0.0.md">Learn More about OpenAPI V3 Specification <i class="fa fa-external-link-square" aria-hidden="true"></i></a>
                        <br />
                        <router-link to="/guide" class="green-text underlined">Use our guide to help you convert your API to OpenAPI V3 specification.</router-link>
                        </div>
                        <hr />
                    </template>
                    <div class="d-flex padding20" style="justify-content: center;">
                        <div class="blue-grey-text grey lighten-4 p-1"><small>API ID</small></div>
                        <div class='grey lighten-3 p-1 indigo-text'><small v-text="selectedAPI._id"></small></div>
                        <CopyButton
                        copy_msg="API ID copied" 
                        :copy="selectedAPI._id">
                            <template v-slot:title>
                                Copy API ID <i class="fa fa-clipboard" aria-hidden="true"></i>
                            </template>
                        </CopyButton>
                    </div>
                    <router-link :to="'/ui/'+selectedAPI._id" class="btn blue m-2">View API Documentation</router-link>
                    <router-link :to="'/registry?q='+selectedAPI._id" class="btn indigo m-2">View API On SmartAPI Registry</router-link>
                    </li>
                    
                </ul>
                </div>

                <div v-show="tabSelected == 2" id="test2" class="col s12 white">
                <div class="row">
                    <div class="col s12 m12 l12 center-align">
                    <h3 class="flow-text blue-grey-text padding20">Slug Registration Wizard</h3>
                    </div>
                    <div v-if='!hasShortName' class="col s12 m12 l12 center-align">
                    <Image class="hide-on-small-only" img_width="100px" img_name="wand.svg" alt='custom slug' style='border-radius: 10px;'></Image>
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
                            <a :href=" 'http://'+selectedAPI._meta.slug+'.smart-api.info'" target="_blank" class="green-text link">http://<b>{{selectedAPI._meta.slug}}</b>.smart-api.info <i class="fa fa-external-link-square" aria-hidden="true"></i></a>
                            <br />
                            <hr />
                            <a class="btn green smallFont margin20" @click.prevent='createOrEditMode = !createOrEditMode'>Edit Slug</a>
                            <a v-if="hasShortName" class="btn red smallFont margin20" @click.prevent='deleteSlug'>Delete Slug</a>
                        </div>
                    </div>
                    <div v-if="createOrEditMode && !hasShortName" style="width: 100%; display: flex; align-items: center;justify-content: center; flex-wrap: wrap;">
                        <div class="left-align padding20 grey-text" style="flex: 1; min-width: 100%;">
                            Slug length must be 4-50 characters (a-z) and/or numbers (0-9). Slugs will be converted to lower case. URL protected characters not allowed.
                        </div>
                        <div style="flex: 1; min-width: 200px;">
                            <input autocomplete="false" v-model='myShortName' placeholder="Enter your slug here" type="text" class="disabled browser-default margin20 grey lighten-5 blue-grey-text lighter" style="width: 85%; outline: none; padding: 10px; border-radius: 20px; border:var(--blue-medium) 2px solid;">
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
                            <button type="button" class="btn" @click.prevent="setShortname" :disabled='!availableShortName && !hasShortName' :class="!availableShortName ? 'grey' : 'green white-text' " >Set Slug</button>
                        </div>

                        <div id="shortNameSuccess" class="center-align padding20 green smallFont" style="flex: 1; min-width: 100%; display: none;">
                            <h5 class="white-text"><i class="fa fa-check white-text" aria-hidden="true"></i> Slug Registered</h5>
                            <a href="javascript:void(0)" class="btn green modal-action modal-close">Close</a>
                        </div>
                    </div>
                </div>
                </div>

                <div v-show="tabSelected == 3" id="test3" class="col s12 white">
                    <div class="row">
                        <div class="col s12 m12 l12 center-align">
                            <h3 class="flow-text blue-grey-text padding20">User Interactions</h3>
                        </div>
                        <div>
                            <SummaryChart :key='selectedAPI.info.title' :data="[]" summary_type="User_Interactions" :colors="['#20c96a', '#2c98f0', '#4bc0c0', '#8d5bd4']" :apiname='selectedAPI.info.title'></SummaryChart>
                            <div>
                                <small>Views = Viewed API details on regsitry, Documentation = Viewed API documentation, Searched = Searched API by name</small>
                            </div>
                        </div>
                    </div>
                </div>
                <div v-show="tabSelected == 4" id="test4" class="col s12 white">
                    <ul class="collection with-header">
                        <li class="collection-item deep-orange lighten-2">
                            <h5>Danger Zone</h5>
                            <p>
                                Delete API metadata from SmartAPI registry permanently. This action cannot be undone.
                            </p>
                            <button type="button" @click="deleteForever(selectedAPI.info.title, selectedAPI._id)" class="btn btn-small red white-text" 
                            data-tippy-content="<b class='red-text'>Delete Forever</b>">
                                Delete API
                            </button>
                        </li>
                    </ul>
                </div>
              </div>
            </div>
        </div>
    </VModal>

    </main>
</template>

<script>
import { mapGetters } from 'vuex'
import moment from 'moment';
import {sortBy, get} from 'lodash'
import tippy from 'tippy.js';
import axios from 'axios'

import UptimeStatus from '../components/UptimeStatus.vue';
import SourceStatus from '../components/SourceStatus.vue';
import SummaryChart from '../components/SummaryChart.vue';

export default {
    name: "DashBoard",
    components:{
        UptimeStatus,
        SourceStatus,
        SummaryChart
    },
    data: function(){
    return {
        confirmModal:{
            title:'',
            id:''
        },
        selectedAPI:Object,
        tabSelected: 1,
        inputApiName:'',
        apis:[],
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
        loading: false,
        // analytics
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
        checkUptime(id){
            let self = this;
            self.showLoading();
            self.$toast.info(`Please wait`);
            if (id) {
                var bodyFormData = new FormData();
                bodyFormData.append('id', id);
                axios({
                    method: "post",
                    url: '/api/uptime',
                    data: bodyFormData,
                    headers: { "Content-Type": "multipart/form-data" },
                }).then(res=>{
                    self.hideLoading();
                    self.$swal({
                        imageUrl: require('../assets/img/api-sucess.svg'),
                        imageWidth: 200,
                        title: 'Your report is ready:',
                        footer: "<p class='green-text'>" + res.data.details + "</p>"
                    })
                }).catch(err=>{
                if(err?.response?.data){
                    self.hideLoading();
                    self.$swal({
                        title: "Oops, there's an issue!",
                        imageUrl: require('../assets/img/api-fail.svg'),
                        imageWidth: 200,
                        confirmButtonText: 'OK',
                        html:`<h5>Here's what we found:</h5>
                            <div class="padding20 orange lighten-5 codeBox"><code>`+err.response.data.details || err.response.data+`</code></div>`,
                        footer:`<p><b class="red-text">Need help?</b> Learn more about and look at examples of SmartAPI extensions <a href="https://github.com/NCATSTranslator/translator_extensions" target="_blank" rel="nonreferrer">here</a>.</p>`
                    })
                }
                });
            } else {
                self.$toast.error('ID is required')
            }
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
                imageUrl: require('../assets/img/api-sucess.svg'),
                imageWidth: 200,
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
                imageUrl: require('../assets/img/api-overwrite.svg'),
                imageWidth: 200,
                confirmButtonText: 'OK',
            });
            }
            else if(err.response.data?.details && err.response.data.details == "API exists"){
            self.$swal({
                title: "Wait a second...",
                html:'<h3>Looks like this API already exists</h3><p>If you are the owner of this API you can refresh it via the <a href="/dashboard">user dashboard</a></p>',
                imageUrl: require('../assets/img/api-fail.svg'),
                imageWidth: 200,
                confirmButtonText: 'OK',
            });
            }
            else if(err.response.data?.details && err.response.data.details.includes("Validation Error")){
            self.$swal({
                title: "Oh no, there's a problem!",
                imageUrl: require('../assets/img/api-fail.svg'),
                imageWidth: 200,
                confirmButtonText: 'OK',
                html:`<h5>Here's what we found:</h5>
                    <div class="padding20 orange lighten-5 codeBox"><code>`+err.response.data.details || err.response.data+`</code></div>`,
                footer:`<p><b class="red-text">Need help?</b> Take a look at OpenAPI specification examples <a href="https://github.com/NCATSTranslator/translator_extensions" target="_blank" rel="nonreferrer">here</a>.</p>`
            })
            }
            else{
            self.$swal({
                title: "Oops, there's an issue!",
                imageUrl: require('../assets/img/api-fail.svg'),
                imageWidth: 200,
                confirmButtonText: 'OK',
                html:`<h5>Here's what we found:</h5>
                    <div class="padding20 orange lighten-5 codeBox"><code>`+err.response.data.details || err.response.data+`</code></div>`,
                footer:`<p><b class="red-text">Need help?</b> Learn more about and look at examples of SmartAPI extensions <a href="https://github.com/NCATSTranslator/translator_extensions" target="_blank" rel="nonreferrer">here</a>.</p>`
            })
            }
            }
            });
        } else {
            self.$toast.error('URL is required')
        }
        },
        getApis: function(){
        var self=this;

        self.apis=[];
        let url = this.$apiUrl + "/query?size=100&q=_meta.username:"+self.userInfo.login

        axios.get(`${url}&timestamp=${new Date().getTime()}&raw=1`).then(function(response){
                self.apis = sortBy(response.data.hits,'info.title');
                self.total = response.data.total;
                self.hideLoading();

            }).catch(err=>{
                self.$toast.error('failed to load APIs')
                self.hideLoading();
                throw err;
            });

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
                self.$swal({
                    title: "Oh no!",
                    confirmButtonText: 'OK',
                    imageUrl: require('../assets/img/api-error.svg'),
                    imageWidth: 200,
                    html: title + " failed to delete."
                })
            }
        }).catch(error=>{
            //error deleting
            throw(error);
        });
        self.getApis();

        },
        showMessage(title, status){
        switch (status) {
            case 'updated':
            this.$swal({
                title: "Sweet!",
                confirmButtonText: 'OK',
                imageUrl: require('../assets/img/api-sucess.svg'),
                imageWidth: 200,
                html: "<h5><b>"+title+"</b> was updated!</h5>",
                footer: "<p>You may look at your latest changes on our <a href='/registry?q="+title+"'>API registry</a>.</p>"
            })
            break;

            case 'not_modified':
            this.$swal({
                title: "Hmmm...",
                imageUrl: require('../assets/img/api-thinking.svg'),
                imageWidth: 200,
                confirmButtonText: 'OK',
                html: "<h5><b>"+title+"</b> has no changes.</h5>",
                footer: "<p>If this doesn't sound right, wait a few minutes and try again. Repositories such as GitHub may have a delay updating their raw data.</p>"
            })
            break;

            case 'invalid':
            this.$swal({
                title: "Oops!",
                confirmButtonText: 'OK',
                imageUrl: require('../assets/img/api-fail.svg'),
                imageWidth: 200,
                html: "<h5 class='red-text'>New version found but there's validation errors.</h5>",
                footer: "<p>Click on <b class='indigo-text'>Validate Only</b> to see validation results. Once they are resolved you can <b class='green-text'>Refresh</b> and synchronize your metadata to its latest version.</p>"
            })
            break;

            case 'nofile':
            this.$swal({
                title: "Oh no!",
                confirmButtonText: 'OK',
                imageUrl: require('../assets/img/api-error.svg'),
                imageWidth: 200,
                html: "<h6 class='red-text'>Looks like the source file no longers exists or is not reachable</h6>",
                footer: "<p>This issue can only be resolved by restoring your source file or deleting this API and re-registering as a new API with a working source file.</p>"
            })
            break;
    
            default:
                self.$toast.error(title,status)
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
                this.$swal({
                    title: "Oh no!",
                    confirmButtonText: 'OK',
                    imageUrl: require('../assets/img/api-error.svg'),
                    imageWidth: 200,
                    html: title + " failed to refresh."
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
        getDetails: function(api){
            this.showModal = true;
            //modal will show the apis index of the item clicked
            this.selectedAPI = api;
            this.tabSelected = 1;
            //hasShortName sets display for slug registration view
            if (this.selectedAPI?._meta?.slug && this.selectedAPI?._meta?.slug.length) {
                this.hasShortName=true;
            }else{
                this.hasShortName=false;
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
        axios.get(`/api/query?q=_meta.slug:"`+this.myShortName+`"&fields=_meta&raw=1`).then(response=>{
            //console.log(response.data.hits);
            if (response.data.total) {
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
        axios.put('/api/metadata/'+self.selectedAPI._id+'?slug='+self.myShortName).then(response=>{
            if( response.data.success ){
                self.selectedAPI._meta.slug= self.myShortName;
                self.myShortName = '';
                self.createOrEditMode = false;
                self.hasShortName = true;
                self.loading = true;

                self.$toast.success(`Slug registered`);

                self.$swal.fire({
                    type:'success',
                    title: "Slug Registered",
                    html:
                        "Hold on while we update your dashboard in <strong></strong> seconds...",
                    timer: 3000,
                    onBeforeOpen: () => {
                        const content = self.$swal.getContent()
                        content.querySelector.bind(content)
                        self.$swal.showLoading()
                        setInterval(() => {
                        self.$swal.getContent().querySelector('strong')
                            .textContent = (self.$swal.getTimerLeft() / 1000)
                            .toFixed(0)
                        }, 100)
                    },
                    onClose: () => {
                        //reload
                        self.$router.go()
                        self.selectedAPI = {}
                    }
                });
                    
                
            }else if( !response.data.success ){
            self.loading = false;
                self.$swal({
                    title: "Oh no!",
                    confirmButtonText: 'OK',
                    imageUrl: require('../assets/img/api-error.svg'),
                    imageWidth: 200,
                    html: response.data?.error
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
        axios.put('/api/metadata/'+self.selectedAPI._id+"?slug=").then(response=>{
            if( response.data.success ){
                self.selectedAPI._meta.slug= '';
                self.createOrEditMode = false;
                self.hasShortName = false;
                self.loading = true;
                //reload
                self.$router.go()
                self.selectedAPI = {}
            }else if( !response.data.success ){
            self.loading = false;
                    self.$swal({
                        title: "Oh no!",
                        confirmButtonText: 'OK',
                        imageUrl: require('../assets/img/api-error.svg'),
                        imageWidth: 200,
                        html: 'slug could not be registered'
                    })
            }
        }).catch(error=>{
            self.$swal({
                        title: "Oh no!",
                        confirmButtonText: 'OK',
                        imageUrl: require('../assets/img/api-error.svg'),
                        imageWidth: 200,
                        html: 'slug could not be registered'
                    })
            throw error;
        });
        }
    },
    mounted: function(){
        this.showLoading();
        this.getApis();

        /*eslint-disable */
        tippy('.tipped',{
            placement: 'top',
            appendTo: document.body,
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

<style>
.dashHead{
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
}
</style>