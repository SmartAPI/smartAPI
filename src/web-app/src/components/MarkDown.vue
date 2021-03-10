<template>
  <div>
    <a v-if="editLink" class="right" :href="editLink" target="_blank" rel="noreferrer">
      <small><i class="fa fa-pencil-square-o" aria-hidden="true"></i> Edit These Docs</small>
    </a>
    <div class="white" v-html="html">
    </div>
  </div>
</template>

<script>
import { Remarkable } from 'remarkable'
import axios from 'axios'

export default {
    name: 'MarkDown',
    data: function () {
      return {
        html: ''
      }
    },
    props:{
        url: {
          required: true,
          type: String
        },
        editLink: {
          type: String,
          default: ''
        }
    },
    methods:{
        convertMarkdownToHtml: function(){
            let self = this;
            axios.get(self.url).then(response=>{
                var md = new Remarkable('full');
            
                md.set({
                  html:         true,        // Enable HTML tags in source
                  breaks:       true,        // Convert '\n' in paragraphs into <br>
                  langPrefix:   'language-',  // CSS language prefix for fenced blocks
                  typographer:  false,
                  quotes: '“”‘’',
                })

                self.html = md.render(response.data);

            }).catch(err=>{
                self.html  = '<h5>Failed to load markdown from ' + self.url + '</h5>'
                throw err;
            });
        },
    },
    watch:{
      url : function(v){
        if(v){
          this.convertMarkdownToHtml()
        }
      }
    },
}
</script>