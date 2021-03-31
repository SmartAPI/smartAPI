<template>
<main id="editor-app" class="white" style="min-height: 100vh;">
    <MetaHead title="SmartAPI | API Editor"></MetaHead>
    <div id="swagger-editor" class="grey lighten-4"></div>
</main>
</template>

<script>
import SwaggerEditorBundle from "swagger-editor"

export default {
    name: "Editor",
    data: function(){
        return {
          apiID:'',
          smartStyle: true,
          context: {}
        }
      },
      methods: {
        loadSwaggerEditor: function(myUrl){
            /* global SwaggerEditorStandalonePreset*/

            const editor = SwaggerEditorBundle({
                url: myUrl,
                dom_id: '#swagger-editor',
                layout: 'StandaloneLayout',
                deeplinking: true,
                presets: [
                    SwaggerEditorStandalonePreset
                ]
            })

          window.editor = editor;

          document.querySelector('#swagger-editor .topbar-logo__img').setAttribute('src', require('../assets/img/logo-medium.svg'));
          document.querySelector(".topbar a[href$='#']").setAttribute('href', 'https://smart-api.info/registry');
      },

    },
    computed:{
        smartapi_id: function(){
            return this.$route.params.smartapi_id
        }
    },
    mounted: function(){
    if(!localStorage.getItem("DontShow")) {
        this.$swal({
            imageUrl: require('../assets/img/api-editor.svg'),
            imageWidth: 200,
            title:'API Editor',
            html:'<h5>What is this?</h5><p>Here you can design, describe, and document your API with this open source editor fully dedicated to OpenAPI-based APIs.</p>',
            showDenyButton: true,
            showConfirmButton: false,
            showCancelButton: false,
            confirmButtonText: `Got It`,
            denyButtonText: `Don't Show Again`,
            }).then((result) => {
            if (result.isConfirmed) {
                //do nothing
            } else if (result.isDenied) {
                localStorage.setItem("DontShow", "true");
            }
            })
    }

    if (this.smartapi_id){
        this.apiID = this.smartapi_id;
        this.loadSwaggerEditor('/api/metadata/'+this.apiID+'?format=yaml');
    }else{
        this.loadSwaggerEditor('https://petstore.swagger.io/v2/swagger.json');
    }

    }

}
</script>

<style>
    #swagger-editor .topbar{
    background-color: #3f85bb;
    }

    * {
    box-sizing: border-box;
    }

    .swagger-ui .info .title small{
    line-height: normal;
    }

    .container {
    height: 100%;
    max-width: 880px;
    margin-left: auto;
    margin-right: auto;
    }

    #editor-wrapper {
    height: 100%;
    border:1em solid #000;
    border:none;
    }

    .Pane2 {
    overflow-y: scroll;
    background-color: white !important;
    }
</style>