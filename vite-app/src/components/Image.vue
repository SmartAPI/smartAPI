<template>
  <object
    :width="img_width"
    :height="img_height"
    alt="SmartAPI"
    :data="getImagePath(img_name)"
  ></object>
</template>

<script>
export default {
  name: 'Image',
  props: {
    img_width: {
      type: String,
      default: 'auto'
    },
    img_name: String,
    img_height: {
      type: String,
      default: 'auto'
    }
  },
  methods: {
    getImagePath(name) {
      return name && !name.includes('http') ? `@/assets/img/${name}` : name
    }
  }
}
</script>
