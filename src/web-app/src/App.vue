<template>
  <teleport to="head">
    <MetaHead></MetaHead>
  </teleport>
  <Navigation></Navigation>
  <div id="modals-go-here"></div>
  <router-view :key="$route.path"/>
  <Footer></Footer>
</template>

<script>
// @ is an alias to /src
import Navigation from '@/components/Navigation.vue'
import Footer from '@/components/Footer.vue'
import MetaHead from '@/components/MetaHead.vue'

export default {
  name: 'App',
  components: {
    Navigation,
    Footer,
    MetaHead
  },
}
</script>