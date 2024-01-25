<template>
  <Navigation></Navigation>
  <!-- <metainfo>
    <template v-slot:title="{ content }">{{ content }} - Yay!</template>
  </metainfo> -->
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
  mounted:function(){
    this.$store.dispatch('loadTagFilters');
    this.$store.dispatch('loadOwnerFilters');
    this.$store.dispatch('loadTranslatorFilters');
  }
}
</script>