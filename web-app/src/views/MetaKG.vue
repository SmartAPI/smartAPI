<template>
  <main id="meta-app" class="white" style="width: 100%;" v-cloak>
  <div class="loadBlock row" v-if="loading && !apisProcessed">
    <div class="col s12 m2 center d-flex align-items-center">
      <i class="fa fa-cog fa-spin fa-fw fa-3x"></i>
    </div>
    <div class="col s12 m10 center">
      <h6 class="grey-text">
        This process might take a several seconds.
      </h6>
      <h6 class="white-text">
        <i class="fa fa-cog fa-spin fa-fw"></i> Getting API metadata..
      </h6>
      <h6 class="white-text">
        <i class="fa fa-cog fa-spin fa-fw"></i> Processing operations from metadata...
      </h6>
    </div>
  </div>
  <div class="p-1 grey lighten-3">
    <div class="center-align" style="margin-bottom:8px;">
      <h6 style="margin:5px; display:inline;">
        <img />
          <Image class="scale-in-center" img_name="metakg-01.png" img_width="30px"
          style="max-width: 50px; max-height: 50px;" ></Image>
        Meta-<b>KG</b>
      </h6>
      <span class="center-align p-1 green white-text rounded" style="margin-right:20px !important;">
        Component:
        <select class="browser-default component-select" v-model='component_select'>
          <option value="" disabled selected>Switch to Component</option>
          <option value="KP">KP</option>
          <option value="ARA">ARA</option>
        </select>
      </span>
      <a href="https://smart-api.info/api/metakg" target="_blank" rel="noreferrer" style="margin-left:20px !important;">
        <small>Download Meta-KG dump</small>
      </a>
    </div>
    <!-- META KG SEARCH -->
    <div class="row m-0">
      <div class="col s12">
        <form class="meta_kg_form">
          <div class="row m-0">
            <div class="col s12 m4 input-field center">
              <h6 class="white-text lighter" style="margin:2px">
                <i class="fa fa-circle grey-text" aria-hidden="true"></i>
                INPUT TYPE
              </h6>
              <PillBox type="input_type"></PillBox>
            </div>
            <div class="col s12 m4 input-field center">
              <h6 class="white-text lighter" style="margin:2px">
                <i class="fa fa-circle purple-text" aria-hidden="true"></i>
                RELATIONSHIP
              </h6>
              <PillBox type="predicate"></PillBox>
            </div>
            <div class="col s12 m4 input-field center">
              <h6 class="white-text lighter" style="margin:2px">
                <i class="fa fa-circle orange-text" aria-hidden="true"></i>
                OUTPUT TYPE
              </h6>
              <PillBox type="output_type"></PillBox>
            </div>
            <div class="col s12 center-align">
              <button style="margin-bottom:5px;" v-if="!loading" class="btn red" type="button" @click.prevent="reset()">
                Reset
              </button>
            </div>
          </div>
        </form>
      </div>
      
      <div class="col s12">
        <div class="metakg-menu w-100">
          <!-- METAKG MENU -->
          <template v-if="overEdgeLimit">
            <p class="red-text p-1">Results contain over <b v-text="edgeLimit"></b> relationship edges, please refine your query to see all possible relationship edges rendered.</p>
          </template>
          <button class="pointer smallButton m-1 right" @click="download">
            <i class="fa fa-download" aria-hidden="true"></i> Download Image
          </button>
          <button class="pointer smallButton m-1 right" @click="recenterGraph()"><i class="fa fa-dot-circle-o"
              aria-hidden="true"></i> Reset Zoom
          </button>
          <template v-if="results.length == 0">
            <p class="red-text p-1">No Results, Please Refine Your Query</p>
          </template>
          <button class="smallButton white-text m-1" :class="[!showOperations ? 'blue' : 'red']" @click.prevent="showOperations = !showOperations">
            {{showOperations ? 'Hide Operations':'Show Operations ('+numberWithCommas(results.length)+')'}}
          </button>
        </div>
      </div>
    </div>

    <div class="d-flex">
      <!-- GRAPH and RESULTS-->
      <div class="col m4 operations-menu p-1" v-if="showOperations">
        <div v-show="results && results.length" class="collection-item green-text" style="padding: 1px;">
          <small>
            <b>{{numberWithCommas(results.length)}}</b> operations
          </small>
        </div>
        <PaginatedList v-if="results && results.length" :content="results" type="MetaKG"></PaginatedList>
      </div>
      <div id="cy">
        <div v-if="loading" class="center">
          <div class="center-align">
            <div class="lds-ellipsis"><div></div><div></div><div></div><div></div></div>
          </div>
        </div>
      </div>
    </div>

    <div class="grey lighten-2 rounded p-1 m-2">
      <div class="container">
        <div>
          <button class="pointer smallButton m-1" @click="showSettings = !showSettings">
            <i class="fa fa-cog" aria-hidden="true"></i> Performance Settings
          </button>
          <div v-if="showSettings" class="p-1 white rounded collection blue-text">
            <div class="collection-item yellow lighten-3 red-text">
              Please allow enough time to update after clicking on each setting
            </div>
            <div class="collection-item">
              <input type="checkbox" id="test1" v-model="SR" @click="toggleSR"/>
              <label for="test1">
                <small>Check to render relationships by <b class="black-text">self-referencing nodes</b>. This requires a differernt method of rendering impacting performance <b>negatively</b>.</small>
              </label>
            </div>
            <div class="collection-item">
              <input type="checkbox" id="withLimit" v-model="edgeLimitBool" @click="withLimit = !withLimit"/>
              <label for="withLimit">
                <small>Click here to enforce <b class="black-text">max number of edges (1,500)</b> to <b>improve</b> performance</small>
              </label>
            </div>
          </div>
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
        'component_select': '',
        'showOperations': false,
        'SR': false,
        'withLimit': false,
        'showSettings': false
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
      },
      edgeLimitBool: function(){
        return this.$store.getters.getLimitBool
      }
    },
    watch: {
      withLimit: function (v) {
        v ? this.$store.commit('setMax', {value: 1500}) : this.$store.commit('setMax', {value: 0})
        this.$toast.success('Updating Results...');
        setTimeout(()=>{this.$store.dispatch('handle_metaKG_Query_New')}, 1000);
      },
      apis: function (a) {
        var self = this;
        if (a.length) {
          self.apisProcessed = true;
        }
      },
      overEdgeLimit: function(v){
        if(v > 0){
          this.$toast.info('Over '+this.edgeLimit+' edge limit');
        }
      },
      component_select: function(v){
        this.$router.push({path: '/portal/translator/metakg/'+v})
      },
    },
    methods: {
      toggleSR(){
        this.$store.commit('toggleSelfReferenced');
        this.$toast.success('Updating Display...');
        setTimeout(()=>{this.$store.commit('drawGraph')}, 1000);
      },
      numberWithCommas(x) {
          return x.toString().replace(/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g, ",");
      },
      allWithTag: function (name) {
        this.$store.dispatch('allWithTag', {highlight: name})
      },
      allWithTagUndo: function () {
        this.$store.dispatch('allWithTagUndo')
      },
      handleME: function (name) {
        this.$store.dispatch('highlightThis', {highlight: name})
      },
      handleML: function (name) {
        this.$store.dispatch('unhighlightThis', {unhighlight: name})
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
        console.log(`%c 🦄 Meta-KG loaded in ${seconds} seconds.`, 'background-color:purple; color:white; padding:5px;');

        //send graph data to store for processing
        this.$store.commit('saveMetaKG', {'metakg': meta_kg});
        this.$store.commit('loadMetaKG', {'res': meta_kg.ops});
        this.$store.commit('drawGraph');
        this.$store.commit('getNewOptions', {'res': meta_kg.ops});
        
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
          self.$store.dispatch('handle_metaKG_Query_New')
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
        this.hoverInfo = item
        this.$store.dispatch('highlightRow', {item: item})
      },
      highlightRowAndZoom: function (item) {
        this.hoverInfo = item
        this.$store.dispatch('highlightRowAndZoom', {item: item})
      },
      unhighlightRow: function (item) {
        let edgeName = item['association']['api_name'] + ' : ' + item['association']['predicate'];
        this.$store.dispatch('unhighlightRow', {unhighlight: edgeName, item: item})
      },
      loadExample() {
        this.$store.commit('reset');
        this.$store.commit('pushPill', {type: 'predicate', q: 'treats'});
        this.$store.commit('pushPill', {type: 'output_type', q: 'Disease'});
      },
      recenterGraph() {
        this.$store.dispatch('recenterGraph')
      },
      checkForQuery(){
          let finalURL = window.location.href
          let url = new URL(finalURL);
          this.$store.dispatch('handleParams', {params: url.search.slice(1)});
      }
    },
    mounted: function () {
      if (this.name == 'translator') {
        this.loadKG();
        this.$store.commit('toggleLoading', {loading: true})
      }
      this.component_select = this.component ? this.component : 'KP'
    }
}
</script>

<style>
  .component-select{
    display: inline-block !important;
    width: 100px;
    padding: 2px;
    height: auto;
    background: transparent;
    outline: none;
    border: none;
  }
  #cy {
    width: 90vw;
    height: 800px;
    display: block;
    border: 2px #dddddd solid;
    background-color:white;
    border-radius: 20px;
    overflow: hidden;
    margin: auto;
  }
  .operation-menu{
    position: absolute;
    left: 5px;
    top: 5px;
  }
  .metakg-menu{
    position: relative;
  }
</style>