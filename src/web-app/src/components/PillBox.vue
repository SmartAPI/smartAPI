<template>
  <div>
        <div class="pillBox lighten-4" :class="getBackClass()">
          <form @submit.prevent="handlePillSubmit" style="display:inline;">
            <input 
            style="width: 100%;" 
            :disabled="loading" 
            v-model='q' 
            :class="getBackClass()" 
            class="browser-default pill-input lighten-4" 
            type="text" 
            name="search" 
            :id="type" 
            :placeholder="loading?'Please wait':'Search'" 
            :list="type+'list'" 
            autocomplete="off">
            <datalist :id="type+'list'"></datalist>
          </form>
        </div>
        <div class="padding20">
          <template v-for="pill in selected" :key="pill">
            <div class="pill" :class="getBackClass()" @click="remove(pill)" >
            <span v-text="pill"></span>
            <span class="red-text">&times;</span>
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
        'q': '',
        'lookupResults': [],
      }
    },
    props: ['type'],
    methods: {
      handlePillSubmit() {
        var self = this;

        if (self.options.includes(self.q)) {
          var payload = {};
          payload["type"] = self.type;
          payload["q"] = self.q;
          this.$store.commit('pushPill', payload);
        } else {
          this.$swal({
            type: 'error',
            toast: true,
            title: 'Not an option',
            showConfirmButton: false,
            timer: 1000
          });
        }

        var payload2 = {};
        payload2["name"] = self.type;
        payload2["q"] = self.selected;

        this.$store.commit('saveInput', payload2);
        //temp fix
        this.$store.dispatch('handle_metaKG_Query_New')
        this.$store.dispatch('buildURL');
        self.q = ''
        // this.$store.dispatch('handle_metaKG_Query_New')
      },
      remove(item) {
        var self = this;

        var payload = {};
        payload["type"] = self.type;
        payload["q"] = item;

        this.$store.commit('removePill', payload);
        //temp fix
        this.$store.dispatch('handle_metaKG_Query_New')
        this.$store.dispatch('buildURL');
      },
      getBackClass() {
        var self = this;

        switch (self.type) {
          case 'predicate':
            return "purple";
          case 'input_type':
            return "grey";
          case 'output_type':
            return "orange";
          default:
            return 'white'
        }
      }
    },
    watch: {
      q: function (q) {
        //after selecting from datalist automatically send selection
        //if selection exists
        var self = this;
        if (q && self.options.includes(q)) {
          self.handlePillSubmit();
        }
      },
      options: function (o) {
        var self = this;
        let html = '';
        if (o.length) {
          document.getElementById(self.type + 'list').innerHTML = ''
          for (var i = 0, len = o.length; i < len; i++) {
            let item = o[i]
            html += `<option value="` + item + `">`;
          }
          document.getElementById(self.type + 'list').innerHTML = html
        }
      },
      selected: function (s) {
        var self = this;

        console.log('selected changed', s)
        // load example by watching selected
        this.$store.commit('saveInput', {"name": self.type, "q":s});
        this.$store.dispatch('handle_metaKG_Query_New')
        this.$store.dispatch('buildURL');

      },
    },
    computed: {
      options: function () {
        var self = this;
        switch (self.type) {
          case 'predicate':
            return this.$store.getters.getP_AC
          case 'input_type':
            return this.$store.getters.getI_AC
          case 'output_type':
            return this.$store.getters.getO_AC
          default:
            console.log('NO AUTOCOMPLETE')
            return []
        }

      },
      selected: function () {
        var self = this;
        switch (self.type) {
          case 'predicate':
            return this.$store.getters.getP_Selected
          case 'input_type':
            return this.$store.getters.getI_Selected
          case 'output_type':
            return this.$store.getters.getO_Selected
          default:
            console.log('NO SELECTED OPTIONS')
            return []
        }

      },
      loading: function () {
        return this.$store.getters.getLoading
      },
    },
}
</script>