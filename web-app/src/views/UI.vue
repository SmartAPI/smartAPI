<template>
  <main id="ui-app" class="indexBackground uiBack" style="width: 100%;">
    <template v-if="api && api.info">
      <MetaHead :title="'SmartAPI | '+ api?.info?.title" :description="api?.info?.description"></MetaHead>
    </template>
    <teleport to="#uiView">
      <div v-if="api && api._id" class="d-flex justify-content-around align-items-center p-1">
        <div class="p-1" style="margin-right:10px;">
          <router-link :to="'/registry?q=' + $route.params.smartapi_id">
            View on SmartAPI Registry
          </router-link>
        </div>
        <div class="d-flex justify-content-around align-items-center p-1">
          <SourceStatus style="margin-right:25px" :api="api"></SourceStatus>
          <UptimeStatus :api="api"></UptimeStatus>
        </div>
        <div class="p-1">
          <small class="white-text tracking-in-expand"> Last updated {{ convertDate(api?._meta?.last_updated) }}</small>
        </div>
      </div>
    </teleport>
    <div class="grey lighten-5 z-depth-3" id="swagger-ui" style="overflow: hidden;"></div>
  </main>
</template>

<script>
import SwaggerUI from 'swagger-ui'
import axios from 'axios'
import moment from 'moment';
import UptimeStatus from '../components/UptimeStatus.vue';
import SourceStatus from '../components/SourceStatus.vue';

import "swagger-ui/dist/swagger-ui.css"

export default {
    name: 'UI',
    data: function(){
        return {
          apiID:'',
          name: '',
          api : Object
        }
      },
      components:{
        SourceStatus,
        UptimeStatus
      },
      methods: {
        convertDate: function(timestamp){
          var date = new Date(timestamp);
          date = moment(date).format('LLL');
          return date;
        },
        loadSwaggerUI: function(dataurl){

          const HideEmptyTagsPlugin = () => {
            return {
              statePlugins: {
                spec: {
                  wrapSelectors: {
                    taggedOperations: (ori) => (...args) => {
                      return ori(...args)
                        .filter(tagMeta => tagMeta.get("operations") && tagMeta.get("operations").size > 0)
                    }
                  }
                }
              }
            }
          };

          const ui = SwaggerUI({
              url: dataurl,
              dom_id: '#swagger-ui',
              deepLinking: true,
              presets: [
                SwaggerUI.presets.apis,
              ],
              plugins: [
                SwaggerUI.plugins.DownloadUrl,
                // plug-in to hide empty tags
                HideEmptyTagsPlugin
              ],
              onComplete:()=>{
                let servers_selected = document.querySelector('div.servers label select').value;
                // console.log("severs", servers_selected)
                if (servers_selected) {
                  if (servers_selected.includes('http:') && window.location.protocol == 'https:') {
                    document.querySelector('div.servers label select').insertAdjacentHTML('afterend', '<div class="yellow lighten-4 red-text padding20"> <i class="material-icons">warning</i> Your connection is secure (HTTPS) and the selected server utilizes an insecure communication (HTTP). <br/>This will likely result in errors, please select a matching protocol server or change your connection. </div>')
                  }
                }
              }
            })
            window.ui = ui;
        },
        getMetadata(url){
          let self = this;
          axios.get(url).then(res=>{
              self.api = res.data
          }).catch(err=>{
            throw err;
          });
        }
      },
      mounted: function(){
        this.loadSwaggerUI('/api/metadata/'+this.apiID);
      },
      beforeMount: function(){
        this.apiID = this.$route.params.smartapi_id;
        this.getMetadata('/api/metadata/'+this.apiID+'?raw=1');
      }
}
</script>

<style scoped>
  .info{
    margin:10px;
  }
</style>