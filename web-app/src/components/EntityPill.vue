<template>
  <div class="entityPill" :class="'ep' + badgeID">
    <div :style="{ 'background-color': color }">
      {{ object }}
    </div>
    <div></div>
    <div class="yellow">
      <ul>
        <li v-for="item in subjects_viewed" :key="item">{{ item }}</li>
        <li
          v-if="!viewingAll"
          @click="
            limit = subjects.length;
            viewingAll = true;
          "
          class="blue-text pointer"
        >
          <b>See All ({{ subjects.length }})</b>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EntityPill',
  data: function () {
    return {
      badgeID: Math.floor(Math.random() * 90000) + 10000,
      limit: 7
    };
  },
  props: ['object', 'subjects'],
  computed: {
    color: function () {
      return this.$store.getters.getEntityColor(this.object);
    },
    subjects_viewed: function () {
      if (this.subjects.length < this.limit) {
        return this.subjects;
      } else {
        return this.subjects.slice(0, this.limit);
      }
    },
    viewingAll: function () {
      if (this.subjects.length <= this.limit) {
        return true;
      } else {
        return false;
      }
    }
  }
};
</script>
