<template>
  <main id="ui-app" class="indexBackground uiBack" style="width: 100%;">
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
          api : {}
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
                console.log("severs", servers_selected)
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
            // console.log('res',res.data)
            let data = res.data
            if (data) {
              let meta = null;
              self.api = data
              // Open graph and Meta
              meta = document.createElement('meta');
              meta.setAttribute('property',"og:title");
              self.name = data.info.title
              meta.setAttribute('content',"SmartAPI | "+data.info.title);
              document.getElementsByTagName('head')[0].appendChild(meta);

              meta = document.createElement('meta');
              meta.setAttribute('name',"description");
              meta.setAttribute('content',data.info.description);
              document.getElementsByTagName('head')[0].appendChild(meta);

              meta = document.createElement('meta');
              meta.setAttribute('property',"og:description");
              meta.setAttribute('content',data.info.description);
              document.getElementsByTagName('head')[0].appendChild(meta);

              meta = document.createElement('meta');
              meta.setAttribute('property',"og:url");
              meta.setAttribute('content',window.location.href);
              document.getElementsByTagName('head')[0].appendChild(meta);

              meta = document.createElement('meta');
              meta.setAttribute('property',"og:locale");
              meta.setAttribute('content',"en_US");
              document.getElementsByTagName('head')[0].appendChild(meta);

              // Twitter
              meta = document.createElement('meta');
              meta.setAttribute('name',"twitter:title");
              meta.setAttribute('content',"SmartAPI | "+data.info.title);
              document.getElementsByTagName('head')[0].appendChild(meta);

              meta = document.createElement('meta');
              meta.setAttribute('name',"twitter:url");
              meta.setAttribute('content',window.location.href);
              document.getElementsByTagName('head')[0].appendChild(meta);

              meta = document.createElement('meta');
              meta.setAttribute('name',"twitter:description");
              meta.setAttribute('content',data.info.description);
              document.getElementsByTagName('head')[0].appendChild(meta);

            }

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