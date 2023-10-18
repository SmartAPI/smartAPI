<template>
  <template v-if="loggedIn">
    <router-link class="dashboard_link" to="/dashboard">
      <img class="user_img" :src="userInfo.avatar_url" :alt="userInfo.login" />
      dashboard
    </router-link>
    <a href="/logout?next=/">
      <b class="red-text">Logout</b>
    </a>
  </template>
  <template v-else>
    <a :href="'/oauth?next=' + nextPath">
      <b class="green-text">Login</b>
    </a>
  </template>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
export default {
  name: 'Login',
  methods: {
    ...mapActions(['checkUser'])
  },
  computed: {
    ...mapGetters(['loggedIn', 'userInfo']),
    nextPath: function () {
      return this.$route.path
    }
  },
  mounted: function () {
    this.checkUser()
  }
}
</script>

<style scoped>
.route-active {
  color: white;
  background: linear-gradient(to bottom, rgb(0, 118, 196) 0, rgb(11, 146, 199) 100%);
  background-size: 100% 100%;
}

.dashboard_link {
  border-radius: 4px;
  display: flex;
  align-items: center;
  padding: 5px 10px;
  transition: all 0.4s;
}

.user_img {
  border-radius: 50%;
  width: 30px;
  height: 30px;
  padding: 0;
  box-sizing: border-box;
  margin: 5px;
  border: 1px white solid;
}
</style>
