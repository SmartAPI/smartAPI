<template>
  <div>
    <div class="d-flex justify-content-center">
      <h6
        class="white-text lighter"
        style="margin: 2px; text-transform: capitalize; margin-right: 10px; font-weight: bold"
      >
        <i class="fa fa-circle" :class="'' + getBackClass() + '-text'" aria-hidden="true"></i>
        {{ type }}
      </h6>
      <label class="white-text">
        <input type="checkbox" class="filled-in" v-model="expand" />
        <span style="padding-left: 24px"
          >Expand
          <i
            class="material-icons tiny cyan-text"
            data-tippy-content='Expand category based on <a target="_blank" href="https://biolink.github.io/biolink-model/">Biolink model</a>'
            >info</i
          ></span
        >
      </label>
    </div>
    <div class="pillBox lighten-4 d-flex flex-wrap align-items-center" :class="getBackClass()">
      <form @submit.prevent="handlePillSubmit" class="m-1">
        <input
          :disabled="loading"
          v-model="q"
          :class="getBackClass()"
          class="browser-default pill-input lighten-4 w-100"
          type="text"
          name="search"
          :id="type"
          :placeholder="loading ? 'Please wait' : 'Search'"
          :list="type + 'list'"
          autocomplete="off"
        />
        <datalist :id="type + 'list'"></datalist>
      </form>
      <template v-for="pill in selected" :key="pill">
        <div
          class="smallButton white-text d-inline-block m-1"
          :class="getBackClass()"
          @click="remove(pill)"
        >
          <span v-text="pill"></span>&nbsp;<span class="red-text"><b>&times;</b></span>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PillBox',
  data: function () {
    return {
      q: '',
      lookupResults: []
    }
  },
  props: ['type'],
  methods: {
    handlePillSubmit() {
      var self = this

      self.$toast.success('Updating...')

      setTimeout(function () {
        if (self.options.includes(self.q)) {
          self.$store.commit('pushPill', { type: self.type, q: self.q })
        } else {
          self.$swal({
            icon: 'error',
            toast: true,
            title: 'Not an option',
            showConfirmButton: false,
            timer: 1000
          })
        }

        var payload2 = {}
        payload2['name'] = self.type
        payload2['q'] = self.selected

        self.$store.commit('saveInput', payload2)
        //temp fix
        console.log('%c ✅ SUBMIT ' + self.type, 'color:limegreen')
        // self.$store.dispatch('handleQuery')
        // self.$store.dispatch('buildURL');
        self.q = ''
      }, 500)
    },
    remove(item) {
      var self = this
      self.$toast.success('Updating...')

      setTimeout(function () {
        self.$store.commit('removePill', { type: self.type, q: item })
        console.log('%c ❌ REMOVE ' + self.type, 'color:red')
        // self.$store.dispatch('handleQuery')
        // self.$store.dispatch('buildURL');
      }, 500)
    },
    getBackClass() {
      switch (this.type) {
        case 'predicate':
          return 'purple'
        case 'subject':
          return 'light-green'
        case 'object':
          return 'orange'
        case 'node':
          return 'cyan'
        case 'edge':
          return 'cyan'
        default:
          return 'white'
      }
    }
  },
  computed: {
    options: function () {
      switch (this.type) {
        case 'predicate':
          return this.$store.getters.getPredicateOptions
        case 'edge':
          return this.$store.getters.getPredicateOptions
        case 'subject':
          return this.$store.getters.getSubjectOptions
        case 'object':
          return this.$store.getters.getObjectOptions
        case 'node':
          return this.$store.getters.getObjectOptions
        default:
          console.log('NO AUTOCOMPLETE')
          return []
      }
    },
    selected: function () {
      switch (this.type) {
        case 'predicate':
          return this.$store.getters.getPredicateSelected
        case 'edge':
          return this.$store.getters.getEdgeSelected
        case 'subject':
          return this.$store.getters.getSubjectSelected
        case 'object':
          return this.$store.getters.getObjectSelected
        case 'node':
          return this.$store.getters.getNode_Selected
        default:
          console.log('NO SELECTED OPTIONS')
          return []
      }
    },
    loading: function () {
      return this.$store.getters.loading
    },
    expand: {
      get() {
        return this.$store.getters.expand.includes(this.type)
      },
      set() {
        this.$store.commit('expandThis', this.type)
      }
    }
  },
  watch: {
    q: function (q) {
      //after selecting from datalist automatically send selection
      //if selection exists
      if (q && this.options.includes(q)) {
        this.handlePillSubmit()
      }
    },
    options: function (o) {
      var self = this
      let html = ''
      if (o.length) {
        document.getElementById(self.type + 'list').innerHTML = ''
        for (var i = 0, len = o.length; i < len; i++) {
          let item = o[i]
          html += `<option value="` + item + `">`
        }
        document.getElementById(self.type + 'list').innerHTML = html
      }
    },
    selected: {
      handler(s) {
        // load example by watching selected
        this.$store.commit('saveInput', { name: this.type, q: s })
        console.log(
          '%c Q from WATCHER from ' + this.type,
          'color:white; background-color:' + this.getBackClass() + ';'
        )
        this.$store.dispatch('handleQuery')
        this.$store.dispatch('buildURL')
      },
      deep: true
    },
    expand: function () {
      this.$toast.success('Updating Results...')
      setTimeout(() => {
        this.$store.dispatch('handleQuery')
        this.$store.dispatch('buildURL')
      }, 1000)
    }
  }
}
</script>
