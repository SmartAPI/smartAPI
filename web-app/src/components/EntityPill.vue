<template>
  <div class="entityPill" :class="'ep' + badgeID">
    <div :style="{ 'background-color': color }">
      {{ object }}
    </div>
    <div></div>
    <div class="yellow">
      <ul>
        <li v-for="item in subjects" :key="item">{{ item }}</li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EntityPill',
  data: function () {
    return {
      badgeID: Math.floor(Math.random() * 90000) + 10000
    };
  },
  props: ['object', 'subjects'],
  computed: {
    color: function () {
      return this.$store.getters.getEntityColor(this.object);
    }
  }
};
</script>
