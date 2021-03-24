<template>
  <main id="registerAPI" class="blue-grey dashboardBack row m-0 darken-2">
    <MetaHead title="SmartAPI | Register Your API"></MetaHead>
  <div class="section no-pad-bot single_section col l12 s12" style="margin-bottom: 10% !important; margin-top: 5%;">
      <div id="submitBox" class="container center-align white hoverable padding20 z-depth-5" style="border-radius: 10px;">
      <Image img_width="200px"  alt="SmartAPI" img_name="api-welcome.svg"></Image>
      <h3 class="center blue-grey-text flow-text">Register your API metadata</h3>
      <form @submit.prevent="handleSubmit()">
          <input placeholder="Enter the URL to your raw API Metadata here" v-model="url" name="url" type="url" class="validate register_input">
          <div class="padding20">
              <input type="checkbox" class="browser-default" id="dry_run" name="dryrun" v-model="dry_run"/>
              <label for="dry_run">Dry run only. API won't actually saved.</label>
              </div>
              <button :class="[ready?'':'hide']" :disabled="!ready" class="btn waves-effect waves-light blue accent-2" id="submit" type="submit">Submit</button>
              <p class="center blue-text">
               If you hosted your data on GitHub make sure to use the raw data link!
               </p>
               <Image img_width="40%" class="hide-on-small-only"  alt="copy the raw data link" img_name="raw.gif"></Image>
               <h4 class="blue-grey-text">Need Help?</h4>
               <p class="blue-grey-text center">
              Use our guide to help you through the process of adding an API.
              <br /><br />
              <router-link to="/guide" class="btn blue">GUIDE</router-link>
              </p>
              <blockquote class="padding20 grey-text">
              Swagger V2 can be submitted, however it will not experience full functionality on SmartAPI and BioThings Explorer.
              <br />
              <a target="_blank" href="https://github.com/SmartAPI/smartAPI-Specification/blob/OpenAPI.next/versions/3.0.0.md">Learn More about OpenAPI V3 Specification <i class="fa fa-external-link-square" aria-hidden="true"></i></a>
              <br />
              <router-link to="/guide"><i class="fa fa-info-circle" aria-hidden="true"></i> Upgrade your Metadata</router-link>
              </blockquote>
              </form>
      </div>
      </div>
</main>
</template>

<script>
import axios from 'axios';
import swal from 'vue-sweetalert2'

export default {
    name: "RegisterAPI",
    data: function(){
        return {
          url:'',
          dry_run: false
        }
      },
      computed:{
        ready: function(){
          return this.url ? true : false;
        }
      },
      methods: {
        handleSubmit: function(){
          let self = this;
          if(self.ready){
            let data = {
              url: self.url
            }
            if(self.dry_run){
              data['dryrun'] = true;
            }
            axios.post("/api", data).then(res=>{
              // console.log('response', res.data)
              if(res.data.success){
                if(Object.prototype.hasOwnProperty.call(res.data, "details") && res.data.details.includes("[Dryrun]")){
                  swal({
                      imageUrl: '/static/img/api-dryrun.svg',
                      imageWidth: 300,
                      imageAlt: 'Dry Run',
                      title: res.data.details,
                      html: "Because this is a dry run your data has <b>not</b> been saved. If you want to register your API, uncheck 'dry run' and try again.",
                    })
                }else if(Object.prototype.hasOwnProperty.call(res.data, "_id")){
                  swal({
                    imageUrl: '/static/img/api-sucess.svg',
                    imageWidth: 300,
                    title: 'Great! You are done!',
                    html: "You can view your API documentation <b><router-link to='/registry?q="+res.data._id+"'>HERE</router-link></b>",
                  })
                }
              }
            }).catch(err=>{
              if(Object.prototype.hasOwnProperty.call(err, "response") && Object.prototype.hasOwnProperty.call(err.response, "data")){
                // console.log('[Error]:', err.response)
                if(Object.prototype.hasOwnProperty.call(err.response.data, "error") && err.response.data.error == "Conflict"){
                swal({
                  title: "Wait a second...",
                  html:'<h3>Looks like this API already exists</h3><p>If you are the owner of this API you can refresh it via the <router-link to="/dashboard">user dashboard</router-link></p>',
                  imageUrl: '/static/img/api-overwrite.svg',
                  imageWidth: 300,
                  confirmButtonText: 'OK',
                });
              }
              else if(Object.prototype.hasOwnProperty.call(err.response.data, "details") && err.response.data.details == "API exists"){
                swal({
                  title: "Wait a second...",
                  html:'<h3>Looks like this API already exists</h3><p>If you are the owner of this API you can refresh it via the <router-link to="/dashboard">user dashboard</router-link></p>',
                  imageUrl: '/static/img/api-fail.svg',
                  imageWidth: 300,
                  confirmButtonText: 'OK',
                });
              }
              else if(Object.prototype.hasOwnProperty.call(err.response.data, "details")  && err.response.data.details.includes("Validation Error")){
                swal({
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
                swal({
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
          }
        }
      },
}
</script>

<style>

</style>