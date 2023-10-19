<template>
  <div class="card-image">
    <img :src="image" width="100%" />
    <img class="pika" src="@/assets/img/api-editor.svg" width="100%" />
  </div>
</template>

<script>
export default {
  name: 'Pikaboo',
  props: ['image']
}
</script>

<style scoped>
.card {
  position: relative;
  overflow: hidden;
}
.card .pika {
  width: 50%;
  opacity: 0;
  position: absolute;
  right: -200px;
  transition: all 0.5s;
}
.card:hover .pika {
  opacity: 1;
  right: -60px;
}
</style>
