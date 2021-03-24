<template>
  <div class="card">
    <div class="card-content ">
          <span class="card-title">
            <span class="blue-grey-text bold" v-text="api.info.title"></span>
            <span class="versionBadge grey" v-text="'V.'+api.info.version">
            </span>
            <span v-if=" api?.openapi " class="versionBadge green">
              OAS3
            </span>
            <span v-else-if=" api?.swagger " class="versionBadge blue">
              Swagger2
            </span>
            <span v-if="api?.info?.['x-trapi']?.version" class="versionBadge pink lighten-2" v-text="'TRAPI '+api?.info?.['x-trapi']?.version">
            </span>
            <span v-if="bt_tag && bt_tag.name == 'biothings' " class="versionBadge grey darken-2">
              BioThings API
            </span>
            <router-link v-if="user && api._meta.username === user.login" 
              :data-tippy-status="api?._status?.refresh_status || 'n/a' "
                to="/dashboard" class="versionBadge light-blue pointer tipped">
              My&nbsp;API 
              <span v-if="api?._status?.refresh_status && ![200, 299, '200', '299'].includes(api?._status?.refresh_status)" 
              class="white-text red" style="padding:2px;border-radius: 4px;margin-left: 5px;">&nbsp;&nbsp;!&nbsp;&nbsp;</span>
            </router-link>
            <UptimeStatus class="right" :api='api'></UptimeStatus>

          </span>
          <template v-if="api.info.description && api.info.description.length > 500">
            <CollapsibleText :text='api.info.description'></CollapsibleText>
          </template>
          <template v-else>
            <div class="blue-grey-text" v-html="compiledMarkdown(api.info.description || '')"></div>
          </template>
          <hr style="border: dotted 1px #e8e8e8 !important;"/>
          <div class="full-width grey-text">
            <template v-for="(tag,index) in api.tags" :key="tag.name">
              <router-link :to="'/registry?tags='+tag.name" @click="googleAnalytics('Registry_Tag', tag.name)" class="blue-text">
                <small>#<span v-text="tag.name"></span></small>
              </router-link>
              <span v-if="index !== api.tags.length-1">, </span>
            </template>
          </div>
      </div>
      <!-- TOGGLE DETAILS -->
      <div class="card-action grey lighten-3" v-if="total > 1" :class="showDetails?'blue':'grey'">
          <button style="border-radius: 20px;" class="btn" :class="showDetails?'grey lighten-3 blue-text':'blue white-text'" @click.prevent="showDetails = !showDetails; googleAnalytics('Registry_APIs',api.info.title)" v-text="showDetails?'HIDE DETAILS':'SHOW DETAILS'"></button>
      </div>
      <div class="card-content detailsBack" v-if="showDetails || total === 1">
        <div class="row">
          <div class="col s12 right-align">
            <small class="grey-text">Updated: </small><small class="white-text"><span v-text="getDate(api._meta.timestamp)"></span></small>
          </div>
          <div class="col s12 left">
            <h4 class="white-text bold m" style="display:inline-block;" v-text="api.info.title"></h4>
            <h5 class="grey-text" style="display:inline-block;">V <span v-text="api.info.version"></span></h5>
          </div>
          <div class="col s12">
            <table class="apiDetails responsive-table">
              <colgroup>
                <col span="1" style="width:25%">
                <col span="1" style="width:75%">
              </colgroup>
              <tbody>
                <tr>
                  <td>
                    <small class="white-text">Created By</small>
                  </td>
                  <td>
                    <small class="white-text">
                      <i class="fa fa-user" aria-hidden="true"></i> <span v-text="api?.info?.contact?.name || 'Name Unavailable'"></span>
                    </small>
                  </td>
                </tr>
                <tr>
                  <td>
                    <small class="white-text">Registered by</small>
                  </td>
                  <td>
                    <small class="white-text">
                      <a :href="'https://github.com/'+api._meta.username" target="_blank" rel="nonreferrer"><i class="fa fa-user" aria-hidden="true"></i> <span v-text="api._meta.username"></span></a>
                    </small>
                  </td>
                </tr>
                <tr>
                  <td>
                    <small class="white-text">SmartAPI ID</small>
                  </td>
                  <td>
                    <a class="link" target="_blank" v-bind:href='"/api/metadata/"+api._id'>
                      <small>
                        <span :id="'id'+api._id" :value="api._id" v-text="api._id"></span> <i class="fa fa-external-link" aria-hidden="true"></i>
                      </small>
                    </a>
                    <button class="smallButton grey copyBtn" :data-clipboard-text="api._id">
                        <i class="fa fa-clipboard" aria-hidden="true"></i>
                    </button>
                  </td>
                </tr>
                <tr>
                  <td>
                    <small class="white-text">Source URL</small>
                  </td>
                  <td>
                    <a class="link" target="_blank" v-bind:href='api._meta.url'>
                      <small><span v-text="truncate(api._meta.url)"></span> <i class="fa fa-external-link" aria-hidden="true"></i></small>
                    </a>
                    <button class="smallButton grey copyBtn" :data-clipboard-text="api._meta.url">
                        <i class="fa fa-clipboard" aria-hidden="true"></i>
                    </button>
                    <a class="smallButton grey" title="Edit metadata source on GitHub" v-if="user && api._meta.username === user.login && api._meta.url.includes('github')" v-bind:href="buildEditURL(api._meta.url)" 
                      target="_blank">
                        <i class="fa fa-pencil" aria-hidden="true"></i>
                    </a>
                    <SourceStatus :api='api'></SourceStatus>
                  </td>
                </tr>
                <tr>
                  <td>
                    <small class="white-text">SmartAPI Registry URL</small>
                  </td>
                  <td>
                    <router-link class="link" target="_blank" :to='"/registry?q="+api._id'>
                      <small><span :id="'url'+api._id" :value="api._id">http://smart-api.info/registry?q=<span v-text="api._id"></span> </span></small>
                    </router-link>
                    <button class="smallButton grey copyBtn" :data-clipboard-text="'http://smart-api.info/registry?q='+api._id">
                        <i class="fa fa-clipboard" aria-hidden="true"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="col s12" style="padding:20px;">
            <router-link class="btn green" style="margin:5px;"
               :to='"/ui/"+api._id' @click="googleAnalytics('Registry_Documentation', api.info.title)">
               <span class="hide-on-small-only">View API</span> Documentation
            </router-link>
            <router-link class="btn blue" style="margin:5px;"
               :to='"/editor/"+api._id'>
               Edit <i class="fa fa-pencil" aria-hidden="true"></i>
            </router-link>
          </div>
        </div>
        <div>
          <template v-if="api?.openapi">
            <h5 class="grey-text">(<span v-text="pathTotal"></span>) Operations</h5>
            <h6 v-if="overLimit">
              <small class="grey-text">This is just a preview. For a full list click on <b class="green-text">View API Documentation</b> link above.</small> 
            </h6>
            <table class="striped responsive-table white" style="margin: 20px 0px;">
              <col width="10%">
              <col width="30%">
              <col width="60%">
              <tbody>
                <tr v-for="operation in getOperations(api)" :key="operation.path">
                  <td class="center-align" :class="operationStyling(operation.method)" v-text="operation.method">
                  </td>
                  <td class="blue-text bold" v-text="operation.path">
                  </td>
                  <td class="blue-grey-text" v-text="operation.summary">
                  </td>
                </tr>
              </tbody>
            </table>
          </template>
        </div>
      </div>
    </div>
</template>

<script>
import SourceStatus from '../components/SourceStatus.vue';
import UptimeStatus from '../components/UptimeStatus.vue';
import CollapsibleText from '../components/CollapsibleText.vue';
import {truncate} from 'lodash'

import marked from 'marked'
import moment from 'moment'

export default {
    name: 'RegistryItem',
    components:{
        SourceStatus,
        UptimeStatus,
        CollapsibleText
    },
    data: function(){
      return{
        showDetails:false,
        overLimit: false,
        pathTotal: 0,
        bt_tag: Object
      }
    },
    props: ['api', 'total', 'user'],
    methods:{
      truncate(text){
        return truncate(text)
      },
      compiledMarkdown: function (mdtext) {
          return marked(mdtext)
      },
      getDate(timestamp){
        var date = moment(timestamp).format("LL");
        return date;
      },
      googleAnalytics(category, label){
        // console.log('category',category,label)
        // this.$gtag.event('click', {'event_category':'general','event_label':label,'event_value':1})

        switch (category) {
          case 'Registry_Tag':
            this.$gtag.event('click', {'event_category':'tag','event_label':label,'event_value':1})
            break;
          case 'Registry_Author':
            this.$gtag.event('click', {'event_category':'author','event_label':label,'event_value':1})
            break;
          case 'Registry_APIs':
            this.$gtag.event('click', {'event_category':'expanded','event_label':label,'event_value':1})
            break;
          case 'Registry_SharedURL':
            this.$gtag.event('click', {'event_category':'shared','event_label':label,'event_value':1})
            break;
          case 'Registry_Searches':
            this.$gtag.event('click', {'event_category':'searched','event_label':label,'event_value':1})
            break;
          case 'Registry_Documentation':
            this.$gtag.event('click', {'event_category':'documentation','event_label':label,'event_value':1})
            break;
          default:
          this.$gtag.event('click', {'event_category':'general','event_label':label,'event_value':1})
        }
      },
      operationStyling: function(op){
        //styles operations based on type
        switch( op.substr(0,3) ){
              case 'GET' :
                return 'bold light-blue darken-1 white-text operation';
              case 'POS' :
                return 'bold light-green white-text operation';
              case 'PUT' :
                return 'bold amber lighten-2 white-text operation';
              case 'DEL' :
                  return 'bold deep-orange darken-1 white-text operation';
              case 'HEA' :
                  return 'bold deep-purple lighten-1 white-text operation';
              case 'PAT' :
                  return 'bold brown lighten-1 white-text operation';
              case 'PAR' :
                  return 'bold teal lighten-1 white-text operation';
              default:
                 return 'bold gray lighten-1 white-text operation'
        }
      },
      buildEditURL: function (raw_url) {
        // build edit github url from raw.githubusercontent type source:
        if(raw_url.includes("raw.githubusercontent")){
          var new_url = raw_url.replace("/raw.githubusercontent.com/","").split("/")
          new_url.splice(3, 0, "edit")
          new_url.splice(1, 0, "/github.com");
          new_url = new_url.join("/")
          return new_url
        }
        // build edit github url from github type source:
        else{
          return raw_url.replace("/raw/","/edit/")
        }
      },
      getOperations: function (api, raw=false) {
        var self= this;
          var operations = [];
          if (raw) {
              for(var path in api.paths) {
                  for(var method in api.paths[path]) {
                      operations.push({'method': self.validateFields(method.toUpperCase()), 'summary': path['pathitem'][method].summary, 'path': path })
                  }
              }
          }else{
              for (let endpoint in api.paths) {
                const item = api.paths[endpoint];
                for(var method2 in item) {
                  if (Object.prototype.hasOwnProperty.call(item[method2], "summary")) {
                    operations.push({'method': self.validateFields(method2.toUpperCase()), 'summary': item[method2]['summary'], 'path': endpoint })
                  }else if (Object.prototype.hasOwnProperty.call(item[method], "description")) {
                    operations.push({'method': self.validateFields(method2.toUpperCase()), 'summary': item[method2]['description'], 'path': endpoint })
                  }
                }
              }
          }
          self.pathTotal = operations.length
          if (self.pathTotal > 20 ) {
            operations = operations.slice(0,19);
            self.overLimit = true
          }
          return operations;
      },
      validateFields(path){
        let paths = ['GET','POST','PUT','DELETE','PATCH','TRACE','HEAD','CONNECT'];
        if (paths.includes(path)) {
          return path;
        }else if (path === "PARAMETERS") {
            return 'GET';
        }
      },
    },
    mounted: function(){
      if(Object.prototype.hasOwnProperty.call(this.api, "tags")){
        this.bt_tag = this.api?.['tags'].find(element => element.name == 'biothings');
      }
    },
}
</script>

<style>

</style>