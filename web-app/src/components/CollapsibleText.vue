<template>
<div>
    <div class="expandContainer" v-bind:class="{'max-height-none' : fullTXT, 'max-height-200': !fullTXT}">

        <div class="center">

        <a class="btn grey lighten-1 expandButtonLess" v-if="fullTXT" @click.prevent="fullTXT = !fullTXT;">
            Collapse
        </a>
        </div>

        <div class="blue-grey-text" v-html="result"></div>

        <div class="center">
        <a class="btn grey lighten-1 expandButtonLess" v-if="fullTXT" @click.prevent="fullTXT = !fullTXT;">
            Collapse
        </a>
        </div>

        <div v-if="!fullTXT" class="whiteFadeBox center">
        <a class="btn grey lighten-1 expandButtonMore" v-if="!fullTXT" @click.prevent="fullTXT = !fullTXT;">Click to expand</a>
        </div>
    </div>
</div>
</template>

<script>
import marked from 'marked'

export default {
    name: 'CollapsibleText',
    data: function(){
      return{
        result:null,
        fullTXT:false
      }
    },
    props: ['text'],
    methods:{
      compileMDWN: function(mdtext){
        this.result = marked(mdtext);
        return this.result;
      }
    },

    mounted: function(){
      this.compileMDWN(this.text)
    },
}
</script>