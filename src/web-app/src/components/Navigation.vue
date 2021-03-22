<template>
  <div class="topnav grey darken-4">
    <router-link to="/" class="topnav-logo">
      <Image img_width="200" alt="SmartAPI Logo" img_name="header-logo.png"></Image>
    </router-link>
    <div id="myLinks" class="hide-on-small-only">
      <router-link to="/add-api">Add an API</router-link>
      <router-link to="/registry">Registry</router-link>
      <router-link to="/editor">Editor</router-link>
      <router-link to="/portal">Portals</router-link>
      <router-link to="/faq">FAQ</router-link>
      <Login></Login>
    </div>
    <a href="javascript:void(0);" class="btn blue hide-on-med-and-up" @click="toggleShow">
      MENU
    </a>
    <div id="myLinksMobile" :class="[show ? 'show-on-small' : 'hide']">
      <div>
        <router-link to="/add-api">Add an API</router-link>
        <router-link to="/registry">Registry</router-link>
        <router-link to="/editor">Editor</router-link>
        <router-link to="/portal">Portals</router-link>
        <router-link to="/faq">FAQ</router-link>
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
}
</script>

<style lang="scss">

  .route-active{
    color: white;
  }

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
    }
    a:hover{
        color: white !important;
      }
  }
</style>
