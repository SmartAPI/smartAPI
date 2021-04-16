<template>
  <Navigation></Navigation>
  <div id="modals-go-here"></div>
  <router-view :key="$route.href"/>
  <Footer></Footer>
</template>

<script>
// @ is an alias to /src
import Navigation from '@/components/Navigation.vue'
import Footer from '@/components/Footer.vue'

export default {
  name: 'App',
  components: {
    Navigation,
    Footer,
  },
}
</script>