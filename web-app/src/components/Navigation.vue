<template>
  <div class="topnav grey darken-4">
    <router-link to="/" class="topnav-logo">
      <Image img_width="200" alt="SmartAPI Logo" img_name="header-logo.png"></Image>
    </router-link>
    <div id="myLinks" class="hide-on-small-only" v-if="!uiView">
      <router-link to="/add-api">Add an API</router-link>
      <router-link to="/registry">Registry</router-link>
      <router-link to="/editor">Editor</router-link>
      <router-link to="/portal">Portals</router-link>
      <router-link to="/faq">FAQ</router-link>
      <Login></Login>
    </div>
    <div id="uiView" v-if="uiView">
      <!-- in UI view status badges will go here -->
    </div>
    <a href="javascript:void(0);" class="hide-on-med-and-up" :class="[show ? 'red-text' : 'blue-text']" @click="toggleShow">
      <i v-if="!show" class="material-icons medium">dehaze</i>
      <i v-else class="material-icons medium fade-in">clear</i>
    </a>
    <div id="myLinksMobile" :class="[show ? 'show-on-small w-100' : 'hide']" v-if="!uiView">
      <div class="fade-in">
        <router-link @click="show = false" to="/add-api">Add an API</router-link>
        <router-link @click="show = false" to="/registry">Registry</router-link>
        <router-link @click="show = false" to="/editor">Editor</router-link>
        <router-link @click="show = false" to="/portal">Portals</router-link>
        <router-link @click="show = false" to="/faq">FAQ</router-link>
        <Login></Login>
      </div>
    </div>
    
  </div>
</template>

<script>
import Login from './Login.vue';

export default {
  name: 'Navigation',
  components:{
    Login,
  },
  data: function(){
    return{
      'show': false
    }
  },
  methods:{
    toggleShow() {
      this.show = !this.show
    }
  },
  computed:{
    uiView:function(){
      return this.$route.name == 'UI' ? true : false;
    }
  }
}
</script>

<style lang="scss">

  .topnav {
    overflow: hidden;
    padding: 4px 10px;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    width: 100vw;
  }

  .topnav-logo{
    display: inline;
  }

  .route-active{
    color: white;
  }

  .topnav #myLinksMobile div{
    display: flex;
    flex-direction: column;
    a{
      padding: 5px;
      align-self: center;
    }
    a:hover{
        color: white !important;
      }
  }

  .topnav #myLinks {
    display: inline-flex;
    a{
      padding: 5px;
      align-self: center;
      margin-right: 10px;
      transition: color .7s;
    }
    a:hover{
        color: white !important;
      }
  }
</style>
