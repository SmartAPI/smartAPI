<template>
  <template v-if="loggedIn">
    <router-link class='dashboard_link' to='/dashboard'>
        <img class='user_img' :src='userInfo.avatar_url' :alt='userInfo.login'>
        dashboard
    </router-link>
    <a href="/logout?next=/">
        <b class="red-text">Logout</b>
    </a>
  </template>
  <template v-else>
    <a href='/oauth'>
        <b class="green-text">Login</b>
    </a>
  </template>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
export default {
    name: "Login",
    methods:{
        ...mapActions([
            'checkUser'
        ])
    },
    computed:{
        ...mapGetters([
            'loggedIn',
            'userInfo'
        ])
    },
    mounted:function(){
        this.checkUser();
    }
}
</script>

<style scoped lang="scss">

    .route-active{
        color: white;
        background: linear-gradient(to bottom, rgba(143, 196, 0, 1) 0, rgba(105, 181, 0, 1)100%);
        background-size: 100% 100%;
    }

    .dashboard_link{
        border-radius: 4px;
        display: flex;
        align-items: center;
        padding: 5px 10px;
        transition: all .4s;
    }
    
    .user_img{
        border-radius: 5%;
        width: 30px;
        height: 30px;
        padding: 0;
        box-sizing: border-box;
        margin: 5px;
        border: 1px white solid;
    }
</style>