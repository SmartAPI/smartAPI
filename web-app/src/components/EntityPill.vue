<template>
  <div class="entityPill" :class="'ep' + badgeID">
    <div :style="{ 'background-color': color }">
      {{ object }}
    </div>
    <div></div>
    <div class="yellow">
      <ul>
        <li v-for="item in subjects_viewed" :key="item">{{ item }}</li>
        <li @click="viewingAll = !viewingAll" class="blue-text pointer">
          <b
            >See {{ viewingAll ? 'Less' : 'More' }}
            <span v-if="!viewingAll">({{ subjects.length }})</span></b
          >
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
      limit: 7,
      viewingAll: false
    };
  },
  methods: {
    toggleViewAll() {
      if (this.limit == this.subjects.length) {
        this.viewingAll = true;
      } else {
      }
    }
  },
  props: ['object', 'subjects'],
  computed: {
    color: function () {
      return this.$store.getters.getEntityColor(this.object);
    },
    subjects_viewed: function () {
      if (this.viewingAll) {
        return this.subjects;
      } else {
        return this.subjects.slice(0, this.limit);
      }
    }
  }
};
</script>
