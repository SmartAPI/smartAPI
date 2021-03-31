<template>
  <main id="meta-app" class="white" style="width: 100%;" v-cloak>
  <div class="loadBlock row" v-if="loading && !apisProcessed">
    <div class="col s12 m2 center d-flex align-items-center">
      <i class="fa fa-cog fa-spin fa-fw fa-3x"></i>
    </div>
    <div class="col s12 m10 center">
      <h6 class="grey-text">
        This process might take a few seconds.
      </h6>
      <h6 class="white-text">
        <template v-if="!apisLoaded">
          <i class="fa fa-cog fa-spin fa-fw"></i>
          Getting API metadata..
        </template>
        <template v-else>
          <i class="fa fa-check green-text" aria-hidden="true"></i>
          API metadata loaded
        </template>
      </h6>
      <h6 class="white-text">
        <template v-if="!apisProcessed">
          <i class="fa fa-cog fa-spin fa-fw"></i>
          Processing operations from metadata...
        </template>
        <template v-else>
          <i class="fa fa-check green-text" aria-hidden="true"></i>
          Processed <span v-text="operationsTotal"></span> operations
        </template>
      </h6>
    </div>
  </div>
  <div class="padding20 grey lighten-3">
    <div class="center">
      <h3 class="m-1">
        <img />
          <Image class="scale-in-center" img_name="metakg-01.png" img_width="30px"
          style="max-width: 50px; max-height: 50px;" ></Image>
        Meta-<b>KG</b>
      </h3>
      <small v-show="component" class="center-align red-text" style="margin-right:20px">
        Component: {{component}}
      </small>
      <a href="https://smart-api.info/api/metakg" target="_blank" rel="noreferrer">
        <small>Download Meta-KG dump</small>
      </a>
    </div>
    <hr />
    <!-- META KG SEARCH -->
    <div class="row m-0">
      <div class="col s12">
        <form class="meta_kg_form">
          <div class="row m-0">
            <div class="col s12 m4 input-field center">
              <h5 class="white-text">
                <i class="fa fa-circle grey-text" aria-hidden="true"></i>
                INPUT TYPE
              </h5>
              <div class="center white-text">
                <small>(1 or Many)</small>
              </div>
              <PillBox type="input_type"></PillBox>
            </div>
            <div class="col s12 m4 input-field center">
              <h5 class="white-text">
                <i class="fa fa-circle purple-text" aria-hidden="true"></i>
                RELATIONSHIP
              </h5>
              <div class="center white-text">
                <small>(1 or Many)</small>
              </div>
              <PillBox type="predicate"></PillBox>
            </div>
            <div class="col s12 m4 input-field center">
              <h5 class="white-text">
                <i class="fa fa-circle orange-text" aria-hidden="true"></i>
                OUTPUT TYPE
              </h5>
              <div class="center white-text">
                <small>(1 or Many)</small>
              </div>
              <PillBox type="output_type"></PillBox>
            </div>
            <div class="col s12 center" style="padding-bottom:8px;">
              <button v-if="!loading" class="btn red" type="button" @click.prevent="reset()">
                Reset
              </button>
            </div>
          </div>
        </form>
      </div>
      <div class="col s12 m4">
        <div v-show="results && results.length" class="collection-item red-text" style="padding: 1px;">
          <small>
            <b>{{numberWithCommas(results.length)}}</b> operations
          </small>
        </div>
        <PaginatedList v-if="results && results.length" :content="results" type="MetaKG"></PaginatedList>
      </div>
      <div class="col s12 m8" style="
          overflow: hidden;
          border: white solid 2px;
          margin: auto;
          background: #f2f2f2;
          margin-top: 10px;
        ">
        <div v-if="loading" class="purple-text padding20 center">
          <h4>Loading...</h4>
        </div>
        <div v-if="overEdgeLimit" class="orange lighten-4 red-text center p-1">
          <small>Results contain over <b v-text="edgeLimit"></b> edges, please refine your query to see all possible edges rendered.</small>
        </div>
        <div v-show="!loading" class="d-flex justify-content-around">
          <small class="pointer grey-text" @click="recenterGraph()"><i class="fa fa-dot-circle-o"
              aria-hidden="true"></i> Reset
            Zoom</small>
        </div>
        <div v-if="!loading && results.length == 0" class="deep-orange-text padding20 center">
          <Image img_name="api-error.svg" img_width="150px" alt="oh no.."></Image>
          <h4>No Results, Please Refine Your Query</h4>
        </div>
        <div id="cy"></div>
        <div v-show="showTags" id="tags" class="padding20 d-flex flex-wrap">
          <template v-for="tag in tagList" :key="tag">
            <small style="margin: 1px;" class="pointer s-badge grey-text" @mouseenter="allWithTag(tag)"
              @mouseleave="allWithTagUndo(tag)">
              <i class="fa fa-tag" aria-hidden="true"></i>
              <span v-text="tag"></span>
            </small>
          </template>
        </div>
        <div v-show="!loading" class="text-right container d-flex justify-content-around">
          <small class="pointer grey-text" @click="download">
            <i class="fa fa-download" aria-hidden="true"></i> Download Image
          </small>
        </div>
      </div>
    </div>
  </div>
</main>
</template>

<script>
import PillBox from '../components/PillBox.vue';
import PaginatedList from '../components/PaginatedList.vue';

const MetaKG  = require("@biothings-explorer/smartapi-kg")

export default {
  components: { 
      PillBox,
      PaginatedList
  },
    name: 'MetaKG',
    props: {
      component:{
        type: String,
        default: 'KP'
      }
    },
    data: function () {
      return {
        'cy': null,
        'showAPIS': false,
        'showTags': false,
        'apisProcessed': false,
        'apisLoaded': false,
        'totalApis': 0,
        'hoverInfo': {},
      }
    },
    computed: {
      name: function () {
        return this.$store.getters.getName
      },
      loading: function () {
        return this.$store.getters.getLoading
      },
      apis: function () {
        return this.$store.getters.getAPIS
      },
      operationsTotal: function () {
        return this.$store.getters.getAPITotal
      },
      portal_info: function () {
        return this.$store.getters.getHtml
      },
      results: function () {
        return this.$store.getters.getResults
      },
      i_ac: function () {
        return this.$store.getters.getI_AC
      },
      o_ac: function () {
        return this.$store.getters.getO_AC
      },
      p_ac: function () {
        return this.$store.getters.getP_AC
      },
      cyto_data: function () {
        return this.$store.getters.getCytoData
      },
      spread: function () {
        return this.$store.getters.getSpread
      },
      tagList: function () {
        return this.$store.getters.getTagList
      },
      overEdgeLimit: function(){
        return this.$store.getters.getOverEdgeLimit
      },
      edgeLimit: function(){
        return this.$store.getters.getLimit
      }
    },
    watch: {
      apis: function (a) {
        var self = this;
        if (a.length) {
          self.apisProcessed = true;
        }
      },
      overEdgeLimit: function(v){
        if(v){
          this.$toast.info('Over '+this.edgeLimit+' edge limit');
        }
      }
    },
    methods: {
      numberWithCommas(x) {
          return x.toString().replace(/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g, ",");
      },
      allWithTag: function (name) {
        var payload = {};
        payload["highlight"] = name
        this.$store.dispatch('allWithTag', payload)
      },
      allWithTagUndo: function () {
        this.$store.dispatch('allWithTagUndo')
      },
      handleME: function (name) {
        var payload = {};
        payload["highlight"] = name
        this.$store.dispatch('highlightThis', payload)
      },
      handleML: function (name) {

        var payload = {};
        payload["unhighlight"] = name
        this.$store.dispatch('unhighlightThis', payload)
      },
      async loadKG() {
        var self = this;
        const t0 = performance.now();

        let meta_kg = new MetaKG.default()
        //load meta-kg API graph with reasoner APIs
        /*eslint-disable */
        await meta_kg.constructMetaKG(true, {component: self.component ? self.component : 'KP'});
        /*eslint-enable */
        const t1 = performance.now();
        self.apisLoaded = true;
        //performance check
        var seconds = (((t1 - t0) % 60000) / 1000).toFixed(0);
        console.log(`%c Getting Meta-KG graph took ${seconds} seconds.`, 'color:limegreen');

        //send graph data to store for processing
        this.$store.commit('loadMetaKG', {'graph': meta_kg});
        this.$store.commit('drawGraph');
        this.checkForQuery();
      },
      parseKGData() {
        var self = this;
        let data = [];

        if (self.ops) {

          for (var i = 0; i < self.ops.length; i++) {
            let node1 = { //a
              data: {
                id: self.ops[i]['association']['input_type']
              }
            };
            data.push(node1)

            let node2 = { //b
              data: {
                id: self.ops[i]['association']['output_type']
              }
            };
            data.push(node2)

            let edgeName = self.ops[i]['association']['api_name'] + ':' + self.ops[i]['association']['predicate']

            let edge = { // edge ab
              data: {
                id: edgeName + i,
                source: self.ops[i]['association']['input_type'],
                target: self.ops[i]['association']['output_type']
              }
            };
            data.push(edge)


          }
          console.log('data', data)
        }
      },
      reset() {
        let self = this;
        this.$toast.success('Reseting please wait...');
        setTimeout(function(){
          self.$store.commit('reset');
        }, 1000);  
      },
      getClass(name) {
        switch (name) {
          case "MyGene.info API":
            return 'blue'
          case "MyChem.info API":
            return 'orange'
          case "MyVariant.info API":
            return 'green'
          default:
            return ''
        }
      },
      download() {
        this.$store.dispatch('download');
      },
      highlightRow: function (item) {

        var self = this;

        self.hoverInfo = item

        var payload = {};
        payload['item'] = item
        this.$store.dispatch('highlightRow', payload)
      },
      highlightRowAndZoom: function (item) {

        var self = this;

        self.hoverInfo = item

        var payload = {};
        payload['item'] = item
        this.$store.dispatch('highlightRowAndZoom', payload)
      },
      unhighlightRow: function (item) {

        var payload = {};
        let edgeName = item['association']['api_name'] + ' : ' + item['association']['predicate'];
        payload["unhighlight"] = edgeName;
        payload['item'] = item;
        this.$store.dispatch('unhighlightRow', payload)
      },
      loadExample() {
        this.$store.commit('reset');

        var payload = {};
        payload["type"] = 'predicate';
        payload["q"] = 'treats';

        this.$store.commit('pushPill', payload);

        var payload2 = {};
        payload2["type"] = 'output_type';
        payload2["q"] = "Disease";

        this.$store.commit('pushPill', payload2);

        // TODO not working because watcher not detecting changes

      },
      recenterGraph() {
        this.$store.dispatch('recenterGraph')
      },
      checkForQuery(){
          let finalURL = window.location.href
          let url = new URL(finalURL);

          var payload = {};
          payload["params"] = url.search.slice(1);
          this.$store.dispatch('handleParams', payload);
      }
    },
    mounted: function () {
      var self = this;
      if (self.name == 'translator') {
        self.loadKG();

        let payload = {}
        payload['loading'] = true;
        this.$store.commit('toggleLoading', payload)
      }

    }
}
</script>

<style>

</style>