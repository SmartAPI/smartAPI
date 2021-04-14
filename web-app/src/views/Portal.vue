<template>
  <div>
    <template v-if="name == 'translator'">
      <TranslatorHome></TranslatorHome>
    </template>
  </div>
</template>

<script>
import TranslatorHome from './TranslatorHome.vue';

export default {
  name: "Portal",
  props: ["name"],
  components:{
    TranslatorHome 
  },
}
</script>