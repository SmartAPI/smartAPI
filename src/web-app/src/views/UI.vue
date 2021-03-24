<template>
  <main id="ui-app" class="indexBackground uiBack" style="width: 100%;">
    <template v-if="api">
      <MetaHead :title="'SmartAPI | '+ api?.info?.title" :description="api?.info?.description"></MetaHead>
    </template>
    <div class="grey lighten-5 z-depth-3" id="swagger-ui" style="overflow: hidden;"></div>
  </main>
</template>

<script>
import SwaggerUI from 'swagger-ui'
import axios from 'axios'
import $ from 'jquery'

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
      methods: {
        loadSwaggerUI: function(dataurl){
          let self = this;

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
                // HideEmptyTagsPlugin
              ],
              onComplete:()=>{
                $("hgroup.main").after('<a class="blue" style="padding:5px; border-radius:5px; border:1px grey solid; color:white !important; text-decoration:none;" href="/registry?q='+self.apiID+'">View on SmartAPI Registry</a>');

                let servers_selected = $("div.servers label select").val();
                // console.log("severs", servers_selected)
                if (servers_selected) {
                  if (servers_selected.includes('http:') && window.location.protocol == 'https:') {
                    $("div.servers label select").after('<div class="yellow lighten-4 red-text padding20"> <i class="material-icons">warning</i> Your connection is secure (HTTPS) and the selected server utilizes an insecure communication (HTTP). <br/>This will likely result in errors, please select a matching protocol server or change your connection. </div>')
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
        this.apiID = this.$route.params.smartapi_id;
        this.loadSwaggerUI('https://smart-api.info/api/metadata/'+this.apiID+'?format=yaml');
        this.getMetadata('https://smart-api.info/api/metadata/'+this.apiID);

      }
}
</script>

<style>
    @import "../assets/css/swagger.css";
</style>