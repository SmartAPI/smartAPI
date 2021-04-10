<template>
  <teleport to="head">
    <title>{{title}}</title>
    <meta property="og:site_name" :content="title">
    <meta name="description" :content="description">
    <meta property="og:url" :content="'https://smart-api.info'+path">
    <meta property="og:title" :content="title"/>
    <meta name="description" :content="description" />
    <meta name="twitter:description" :content="description" />
    <meta name="twitter:url" :content="'https://smart-api.info'+path"/>
    <meta property="og:description" :content="description" >
    <meta name="twitter:title" :content="title"/>
    <meta property="fb:app_id" :content="title"/>
    <meta name="twitter:card" :content="description"/>
  </teleport>
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
  }
}
</script>