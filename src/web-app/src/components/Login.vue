<template>
  <template v-if="loggedIn">
    <a class='dashboard_link' href='/dashboard' :class="{'route-active': current == 'Dashboard'}">
        <img class='user_img' :src='userInfo.avatar_url' :alt='userInfo.login'>
        dashboard
    </a>
    <a href="/logout?next='/'">
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
        current: function(){
        return this.$route.name
        },
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

    .dashboard_link{
        background: rgb(51, 51, 51);
        border-radius: 4px;
        display: flex;
        align-items: center;
        padding: 5px 10px;
        transition: all .4s;
        &:hover{
            background: #3F85BB;
        }
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