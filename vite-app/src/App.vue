<script setup>
// @ is an alias to /src
import Navigation from '@/components/Navigation.vue'
import Footer from '@/components/Footer.vue'
import { useStore } from 'vuex'

const store = useStore()

store.dispatch('loadTagFilters')
store.dispatch('loadOwnerFilters')
store.dispatch('loadTranslatorFilters')
</script>

<template>
  <Navigation></Navigation>
  <div id="modals-go-here"></div>
  <router-view :key="$route.href" />
  <Footer></Footer>
</template>
