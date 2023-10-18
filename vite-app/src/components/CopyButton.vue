<template>
  <button
    v-bind="$attrs"
    class="CopyButton copyBtn pointer"
    @click="notify"
    :data-clipboard-text="copy"
    :class="['cp' + badgeID, cls]"
  >
    <slot v-if="!showAnimation" name="title">
      <!-- TITLE -->
    </slot>
    <span v-else>Copied!</span>
  </button>
</template>

<script>
import ClipboardJS from 'clipboard'

export default {
  name: 'CopyButton',
  data: function () {
    return {
      badgeID: Math.floor(Math.random() * 90000) + 10000,
      cls: '',
      showAnimation: false
    }
  },
  props: {
    copy: {
      type: String,
      default: ''
    },
    copy_msg: {
      type: String,
      default: 'Copied to Clipboard'
    },
    tip_msg: {
      type: String,
      default: '<small class="p-1">Click to Copy</small>'
    }
  },
  methods: {
    notify() {
      this.$toast.success(this.copy_msg)
      this.animate()
    },
    animate() {
      let self = this
      this.cls = 'indigo accent-4 white-text'
      this.showAnimation = true
      setTimeout(function () {
        self.cls = ''
        self.showAnimation = false
      }, 1500)
    }
  },
  mounted: function () {
    new ClipboardJS('.copyBtn')
    ClipboardJS.isSupported()
  }
}
</script>

<style>
.CopyButton {
  padding: 2px 5px;
  border-radius: 10px;
  margin-left: 8px;
  background-color: #e0e0e0;
  outline: none;
  box-shadow: none;
  border: none;
  color: #646464;
  font-size: 10px !important;
  transition: all 0.5s;
}
.CopyButton:hover {
  color: white;
  background-color: #3f51b5;
}
.CopyButton:focus {
  color: white;
  background-color: #7986cb;
}
</style>
