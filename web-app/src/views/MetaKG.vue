<template>
  <main id="meta-app" class="white" style="width: 100%;" v-cloak>
  <div class="loadBlock row" v-if="loading">
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
      <router-link to="/portal/translator" class="red-text">
        Back to Portal
      </router-link>
      <h6 style="margin:5px; display:inline;">
        <img />
          <Image class="scale-in-center" img_name="metakg-01.png" img_width="30px"
          style="max-width: 50px; max-height: 50px;" ></Image>
        Meta-<b>KG</b>
      </h6>
      <!-- <span class="center-align p-1 green white-text rounded" style="margin-right:20px !important;">
        Component:
        <select class="browser-default component-select" v-model='component_select'>
          <option value="" disabled selected>Switch to Component</option>
          <option value="KP">KP</option>
          <option value="ARA">ARA</option>
        </select>
      </span> -->
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
                <i class="fa fa-circle indigo-text" aria-hidden="true"></i>
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
          <template v-if="usingCytoscape">
            <button class="pointer smallButton m-1 right" @click="download">
              <i class="fa fa-download" aria-hidden="true"></i> Download Image
            </button>
            <button class="pointer smallButton m-1 right" @click="recenterGraph()"><i class="fa fa-dot-circle-o"
                aria-hidden="true"></i> Reset Zoom
            </button>
          </template>
          <template v-if="results.length == 0">
            <p class="red-text p-1">No Results, Please Refine Your Query</p>
          </template>
          <button class="smallButton white-text m-1" :class="[!showOperations ? 'blue' : 'red']" @click.prevent="showOperations = !showOperations">
            {{showOperations ? 'Hide Operations':'Show Operations ('+numberWithCommas(results.length)+')'}}
          </button>
        </div>
      </div>
    </div>

    <div class="d-flex justify-content-center graph-cont">
      <!-- GRAPH and RESULTS-->
      <div v-if="showOperations" class="col m4 operations-menu p-1">
        <div class="right-align">
          <span class="pointer red-text" @click="showOperations = false">close &times;</span>
        </div>
        <template v-for="item in results" :key="item.id">
          <div class="m-1" @mouseenter="highlightRow(item)" @mouseleave="unhighlightRow(item)" >
            <small v-html="item.data.html"></small>
          </div>
        </template>
      </div>
      <div id="cy" v-if="usingCytoscape">
        <div v-if="loading" class="center">
          <div class="center-align">
            <div class="lds-ellipsis"><div></div><div></div><div></div><div></div></div>
          </div>
        </div>
      </div>
      <div v-else id="3d-graph"></div>
    </div>

    <div class="grey lighten-2 rounded p-1 m-2">
      <div class="container">
        <div>
          <button class="pointer smallButton m-1" @click="showSettings = !showSettings">
            <i class="fa fa-cog" aria-hidden="true"></i> Display Settings
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
                <small>Click here to enforce <b class="black-text">max number of edges (1,500)</b> to <b>improve</b> performance.</small>
              </label>
            </div>
            <div class="collection-item">
              <input type="checkbox" id="usingCytoscape" v-model="usingCytoscape"/>
              <label for="usingCytoscape">
                <small>Click here to render the results using CytoscapeJS instead of using a 3D Model.</small>
              </label>
            </div>
            <div class="collection-item">
              <input type="checkbox" id="usingAPI" v-model="useAPI"/>
              <label for="usingAPI">
                <small>Use SmartAPI API (default) or use SmartAPI KG NPM package (unchecked). If you have any issues please contact us.</small>
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
import axios from 'axios';
import { mapGetters } from 'vuex'

const MetaKG  = require("@biothings-explorer/smartapi-kg")

export default {
  components: { 
      PillBox,
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
        'hoverInfo': {},
        'component_select': 'KP',
        'showOperations': false,
        'SR': false,
        'withLimit': false,
        'showSettings': false
      }
    },
    computed: {
      ...mapGetters([
        'loading',
        'overEdgeLimit',
        'results',
      ]),
      edgeLimit: function(){
        return this.$store.getters.getLimit
      },
      edgeLimitBool: function(){
        return this.$store.getters.getLimitBool
      },
      usingCytoscape: {
        get () {
          return this.$store.getters.usingCytoscape
        },
        set (v) {
          return this.$store.commit('setRenderer', {value: v})
        }
      },
      useAPI: {
        get () {
          return this.$store.getters.useAPI
        },
        set (v) {
          return this.$store.commit('setUseAPI', {value: v})
        }
      }
    },
    watch: {
      withLimit: function (v) {
        v ? this.$store.commit('setMax', {value: 1500}) : this.$store.commit('setMax', {value: 0})
        this.$toast.success('Updating Results...');
        setTimeout(()=>{this.$store.dispatch('handleQuery')}, 1000);
      },
      usingCytoscape: function () {
        this.$toast.success('Updating Results...');
        setTimeout(()=>{this.$store.dispatch('handleQuery')}, 1000);
      },
      overEdgeLimit: function(v){
        if(v > 0){
          this.$toast.info('Over '+this.edgeLimit+' edge limit');
        }
      },
      component_select: function(v){
        this.$store.commit('saveComponent', {'value': v});
        this.$router.push({path: '/portal/translator/metakg/'+v, query: this.$route.query})
      },
      useAPI: function(){
        this.load();
      }
    },
    methods: {
      toggleSR(){
        this.$store.commit('toggleSelfReferenced');
        this.$toast.success('Updating Display...');
        setTimeout(()=>{this.$store.dispatch('draw')}, 1000);
      },
      numberWithCommas(x) {
          return x.toString().replace(/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g, ",");
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
        //performance check
        var seconds = (((t1 - t0) % 60000) / 1000).toFixed(0);
        console.log(`%c 🦄 Meta-KG loaded in ${seconds} seconds.`, 'background-color:purple; color:white; padding:5px;');

        //send graph data to store for processing
        this.$store.commit('saveMetaKG', {'metakg': meta_kg});

        // this.$store.commit('createGraphData', {'res': meta_kg.ops});
        // this.$store.dispatch('draw');
        // this.$store.commit('getNewOptions', {'res': meta_kg.ops});
        // setTimeout(()=>{this.checkForQuery()}, 1000)

        //just let this handle whole initial flow
        this.checkForQuery()
      },
      loadAPIKG(){
        axios.get('https://smart-api.info/api/metakg').then((res) => {
          let data = res.data.associations.map(data => {
            return {'association': data}
          })
          data = data.slice(0, 1500)
          console.log('SAMPLE', data[0])
          this.$store.commit('saveMetaKG', {'metakg': data});
          this.checkForQuery()
        }).catch((err) => {
          throw err;
        })
      },
      load(){
        if (this.useAPI) {
          console.log('using API');
          this.loadAPIKG();
        } else {
          console.log('using KG package');
          this.loadKG();
        }
      },
      reset() {
        let self = this;
        this.$toast.success('Reseting please wait...');
        setTimeout(function(){
          self.$store.commit('reset');
          self.$store.dispatch('handleQuery')
        }, 1000);  
      },
      download() {
        if (this.usingCytoscape) this.$store.dispatch('download');
      },
      highlightRow: function (item) {
        if (this.usingCytoscape) {
          this.hoverInfo = item
          this.$store.dispatch('highlightRow', {item: item})
        }
      },
      highlightRowAndZoom: function (item) {
        if (this.usingCytoscape) {
          this.hoverInfo = item
          this.$store.dispatch('highlightRowAndZoom', {item: item})
        }
      },
      unhighlightRow: function (item) {
        if (this.usingCytoscape) {
          let edgeName = item['association']['api_name'] + ' : ' + item['association']['predicate'];
          this.$store.dispatch('unhighlightRow', {unhighlight: edgeName, item: item})
        }
      },
      recenterGraph() {
        if (this.usingCytoscape) this.$store.dispatch('recenterGraph')
      },
      checkForQuery(){
          let finalURL = window.location.href
          let url = new URL(finalURL);
          this.$store.dispatch('handleParams', {params: url.search.slice(1)});
      }
    },
    mounted: function () {
      this.$store.commit('toggleLoading', {loading: true})
      this.component_select = this.component ? this.component : 'KP'
      this.load();
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
  .operations-menu{
    max-height: 1000px;
    overflow-y: scroll;
    background-color: rgba(137, 32, 179, 0.2);
    position: absolute;
    left: 5px;
    top: 5px;
    z-index: 100;
  }
  .graph-cont{
    position: relative;
    overflow: hidden;
  }
  .metakg-menu{
    position: relative;
  }
  .node-label {
    font-size: 12px;
    padding: 1px 4px;
    border-radius: 4px;
    background-color: rgba(82, 17, 112, 0.7) !important;
    color: white;
    user-select: none;
  }
  .scene-tooltip{
    z-index: 1000;
  }
</style>