<template>
  <!-- <teleport to="head">
    <title>{{title}}</title>
    <meta name="description" :content="description">
    <meta property="og:site_name" :content="title">
    <meta property="fb:app_id" :content="title"/>
    <meta property="og:description" :content="description" >
    <meta property="og:url" :content="'https://smart-api.info'+path">
    <meta property="og:title" :content="title"/>
    <meta name="twitter:description" :content="description" />
    <meta name="twitter:url" :content="'https://smart-api.info'+path"/>
    <meta name="twitter:title" :content="title"/>
    <meta name="twitter:card" :content="description"/>
  </teleport> -->
  <div></div>
</template>

<script>
export default {
  name: 'MetaHead',
  props:{
    title:{
      type: String,
      default: 'SmartAPI'
    },
    description:{
      type: String,
      default: 'The SmartAPI project aims to maximize the FAIRness (Findability, Accessibility, Interoperability, and Reusability) of web-based Application Programming Interfaces (APIs)'
    }
  },
  computed:{
    path:function(){
      return this.$route.fullPath
    }
  },
  mounted: function(){
    //title
    document.querySelector("title").innerHTML = this.title
    document.querySelector("meta[name='twitter:title']").setAttribute('content', this.title);
    document.querySelector("meta[property='og:site_name']").setAttribute('content', this.title);
    document.querySelector("meta[property='fb:app_id']").setAttribute('content', this.title);
    document.querySelector("meta[property='og:title']").setAttribute('content', this.title);
    //desc
    document.querySelector("meta[name='description']").setAttribute('content', this.description);
    document.querySelector("meta[name='twitter:description']").setAttribute('content', this.description);
    document.querySelector("meta[name='twitter:card']").setAttribute('content', this.description);
    //path
    document.querySelector("meta[name='twitter:url']").setAttribute('content', 'https://smart-api.info'+this.path);
    document.querySelector("meta[property='og:url']").setAttribute('content', 'https://smart-api.info'+this.path);
  }
}
</script>