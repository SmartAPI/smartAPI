<template>
  <main id="meta-app" class="white" style="width: 100%;" v-cloak>
  <div class="p-1 grey lighten-3">
    <div class="center-align" style="margin-bottom:8px;">
      <router-link to="/portal/translator" class="red-text left">
        Back to Portal
      </router-link>
      <h6 style="margin:5px; display:inline;">
          <Image class="scale-in-center" img_name="metakg-01.png" img_width="30px"
          style="max-width: 50px; max-height: 50px;" ></Image>
        Meta-<b>KG</b> Explorer
      </h6>
    </div>
    <!-- META KG SEARCH -->
    <div class="row m-0">
      <div class="col s7 pointer" @click="setNodeMode(false)">
      <form :class="[!generalMode ? 'purple darken-3' : 'tab-not-active']" class="top-br">
          <div class="row m-0">
            <div class="col s12 m4 input-field center">
              <PillBox type="subject"></PillBox>
            </div>
            <div class="col s12 m4 input-field center">
              <PillBox type="predicate"></PillBox>
            </div>
            <div class="col s12 m4 input-field center">
              <PillBox type="object"></PillBox>
            </div>
          </div>
        </form>
      </div>
      <div class="col s5 pointer" @click="setNodeMode(true)">
        <form :class="[generalMode ? 'cyan  darken-3' : 'tab-not-active']" class="top-br">
          <div class="row m-0">
            <div class="col s12 m6 input-field center">
              <PillBox type="node"></PillBox>
            </div>
            <div class="col s12 m6 input-field center">
              <PillBox type="edge"></PillBox>
            </div>
          </div>
        </form>
      </div>
      <div class="col s12 top-br lighten-3" :class="[!generalMode ? 'purple' : 'cyan ']">
        <div class="row m-0">
          <div class="col s12 m8">
            <div class="d-flex align-items-center justify-content-around">
              <div class="d-flex align-items-center">
                <p class="p-0">
                  Size
                </p>
                <select class="browser-default size-select white-text"
                :class="[!generalMode ? 'purple' : 'cyan ']" v-model="size">
                    <option value="" disabled>Choose Size</option>
                    <option value="20">20</option>
                    <option value="40">40</option>
                    <option value="100">100</option>
                    <option value="200">200</option>
                    <option value="500">500</option>
                    <option value="1000">1000 (Slow)</option>
                    <option value="1000">5000 (Slower)</option>
                </select>
              </div>
              <div class="lighten-2 p-1 d-flex" style="border-radius: 5px;"  
              :class="[!generalMode ? 'purple' : 'cyan ']" 
              data-tippy-content="Select Translator Component (Default ANY)">
                <div style="margin-right: 10px;">
                  <input type="checkbox" id="ara" v-model="ara"/>
                  <label class="white-text" for="ara">ARAs</label>
                </div>
                <div>
                  <input type="checkbox" id="kp" v-model="kp"/>
                  <label class="white-text" for="kp">KPs</label>
                </div>
                <select class="browser-default" style="border-radius: 5px;" v-if="kp && KPNames?.length" v-model="kpSelected">
                  <option value="" disabled selected>(Optional) Select KP</option>
                  <option v-for="kp in KPNames" :value="kp" :key="kp">{{ kp }}</option>
                </select>
                <select class="browser-default" style="border-radius: 5px;" v-if="ara && ARANames?.length" v-model="araSelected">
                  <option value="" disabled selected>(Optional) Select ARA</option>
                  <option v-for="ara in ARANames" :value="ara" :key="ara">{{ ara }}</option>
                </select>
              </div>
              <form @submit.prevent="search()" class="d-flex flex-wrap align-items-center justify-content-center m-1">
                <input 
                v-model="query_term" 
                type="text" 
                placeholder="(Optional) Query term" 
                style="border-radius: 20px;"
                list="query-input" 
                autocomplete="off"
                class="browser-default mr-1 query-input">
                <datalist id='query-input'></datalist>
                <button v-if="query_term" class="smallButton green white-text" style="margin-right: 10px;" type="submit">Update</button>
                <button v-if="query_term" @click="clear()" class="smallButton red white-text" type="button">Clear</button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="row m-0 lighten-5" :class="[!generalMode ? 'purple' : 'cyan ']">
      <!-- GRAPH and RESULTS-->
      <div class="col s3 p-1 operations-menu grey darken-1" style="padding-bottom: 20px; min-height: 700px;">
        <h6 class="white-text"><b>Overview</b></h6>
        <small class="white-text">Based on the current query: </small>
        <table class="white-text highlight grey darken-2" style="font-size: smaller; margin-bottom: 5px;">
          <thead>
            <th class="p-small"></th>
            <th class="p-small">Shown <i class="material-icons tiny cyan-text" data-tippy-content='Edges and APIs matching current criteria and size constraints.'>info</i></th>
            <th class="p-small">Available <i class="material-icons tiny cyan-text" data-tippy-content='Total edges and APIs available matching search criteria some may not be included due to size constraints set. You can increase size to include more results.'>info</i></th>
          </thead>
          <tbody>
            <tr>
              <td class="p-small">Edges</td>
              <td class="p-small scale-in-center lime-text" v-text="total < size ? numberWithCommas(total) : size"></td>
              <td class="p-small scale-in-center">
                {{ numberWithCommas(total) }}
                <template v-if="results.length < total">
                  <i style="z-index: 100;" class="fa fa-exclamation-circle orange-text m-1" 
                  data-tippy-content="Increase size to view more edges available"
                  title="Increase size to view more edges available"
                  aria-hidden="true"></i>
                </template>
              </td>
            </tr>
            <tr>
              <td class="p-small">Subjects</td>
              <td class="p-small scale-in-center lime-text"> {{ displayedSubjects.length }}</td>
              <td class="p-small scale-in-center">
                <details>
                  <summary>
                    {{ subjectTotalFromResponse.length }}
                  </summary>
                  <ul>
                    <li v-for="item in subjectTotalFromResponse" :key="item.term + 'sub'">{{ item.term }}</li>
                  </ul>
                </details>
              </td>
            </tr>
            <tr>
              <td class="p-small">Objects</td>
              <td class="p-small scale-in-center lime-text">{{ displayedObjects.length }}</td>
              <td class="p-small scale-in-center">
                <details>
                  <summary>
                    {{ objectTotalFromResponse.length }}
                  </summary>
                  <ul>
                    <li v-for="item in objectTotalFromResponse" :key="item.term + 'obj'">{{ item.term }}</li>
                  </ul>
                </details>
              </td>
            </tr>
          </tbody>
        </table>
        <details v-for="hit in results" 
        :key="hit?._id" 
        class="border-b p-1 white edge-summary"
        @mouseenter="highlightRow(hit)" 
        @mouseleave="unhighlightRow(hit)" 
        style="overflow: hidden; border-radius: 5px;">
          <summary>
            <table class="sm-table" style="font-size: x-small;">
              <tr>
                <td>
                    <b> {{ readableName(hit.subject) }}</b>&nbsp;
                    <a target="_blank" :href="'https://biolink.github.io/biolink-model/docs/' + hit.subject">
                      <i class="fa fa-external-link" aria-hidden="true"></i>
                    </a>
                </td>
                <td>
                  <b>
                  {{ readableName(hit.predicate.replaceAll('_', ' ')) }} 
                  <a target="_blank" :href="'https://biolink.github.io/biolink-model/docs/' + hit.predicate">&nbsp;
                    <i class="fa fa-external-link" aria-hidden="true"></i>
                  </a>
                </b>
                </td>
                <td>
                    <b>{{ readableName(hit.object) }}</b>&nbsp;
                    <a target="_blank" :href="'https://biolink.github.io/biolink-model/docs/' + hit.object">
                      <i class="fa fa-external-link" aria-hidden="true"></i>
                    </a>
                </td>
                <td>
                  <b class="green-text"> ({{ hit.api.length }})</b>
                </td>
              </tr>
            </table>
          </summary>
          <table class="edge-table" style="font-size: x-small;">
            <tr 
            v-for="item in hit?.api" :key="item.id" >
                <td>
                  <small>{{ item.name }}</small>
                </td>
                <td>
                  <router-link :to="{path:'/registry', query: {'q': item?.smartapi?.id}}" target="_blank" class="mr-1 p-1">
                    SmartAPI <i class="fa fa-external-link" aria-hidden="true"></i>
                  </router-link>
                </td>
                <td>
                  <router-link :to="{path:'/ui/' + item?.smartapi?.id}" target="_blank" class="mr-1 p-1">
                    Docs <i class="fa fa-external-link" aria-hidden="true"></i>
                  </router-link>
                </td>
            </tr>
          </table>
        </details>
      </div>
      <div class="col s9">
        <div style="position: relative;">
          <div id="cy" style="position: absolute;"></div>
          <div class="graph-btn-container">
              <button class="smallButton white-text m-1" 
              data-tippy-content="Reset Graph Position"
              data-tippy-position="right"
              :class="[!generalMode ? 'purple' : 'cyan ']" 
              @click="recenterGraph()">
                <i class="fa fa-dot-circle-o" aria-hidden="true"></i>
              </button>
              <button class="smallButton white-text m-1" 
              data-tippy-content="Download Image"
              :class="[!generalMode ? 'purple' : 'cyan ']" 
              @click="download">
                <i class="fa fa-download" aria-hidden="true"></i>
              </button>
            <a class="smallButton white-text m-1" 
            data-tippy-content="View Raw Data"
            :href="finalURL"
            target="_blank"
            :class="[!generalMode ? 'purple' : 'cyan ']">
              <i class="fa fa-external-link" aria-hidden="true"></i>
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</main>
</template>

<script>
import PillBox from '../components/PillBox.vue';
import { mapGetters } from 'vuex'

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
        'showOperations': false,
      }
    },
    computed: {
      ...mapGetters([
        'loading',
        'overEdgeLimit',
        'results',
        'KPNames',
        'ARANames',
        'apiTotalFromResponse',
        'subjectTotalFromResponse',
        'objectTotalFromResponse',
        'displayedSubjects',
        'displayedObjects',
        'generalMode',
        'finalURL'
      ]),
      edgeLimit: function(){
        return this.$store.getters.getLimit
      },
      total: function(){
        return this.$store.getters.total
      },
      size: {
        get () {
          return this.$store.getters.size
        },
        set (v) {
          return this.$store.commit('setSize', v);
        }
      },
      kp: {
        get () {
          return this.$store.getters.kp
        },
        set (v) {
          if (!v) {
            // if no KP filter reset KP Selected
            this.$store.commit('setKPSelected', "");
          }
          // toggle KP off
          if (v) {
            this.$store.commit('setARA', false);
            this.$store.commit('setARASelected', '');
          }
          return this.$store.commit('setKP', v);
        }
      },
      kpSelected: {
        get () {
          return this.$store.getters.kpSelected
        },
        set (v) {
          return this.$store.commit('setKPSelected', v);
        }
      },
      araSelected: {
        get () {
          return this.$store.getters.araSelected
        },
        set (v) {
          return this.$store.commit('setARASelected', v);
        }
      },
      ara: {
        get () {
          return this.$store.getters.ara
        },
        set (v) {
          if (!v) {
            // if no KP filter reset KP Selected
            this.$store.commit('setARASelected', "");
          }
          // toggle ARA off
          if (v) {
            this.$store.commit('setKP', false);
            this.$store.commit('setKPSelected', "");
          }
          return this.$store.commit('setARA', v);
        }
      },
      query_term: {
        get () {
          return this.$store.getters.query_term
        },
        set (v) {
          return this.$store.commit('setTerm', v);
        }
      },
    },
    watch: {
      results: function (v) {
        if(!v.length){
          this.$toast.error('No results');
        }
      },
      overEdgeLimit: function(v){
        if(v > 0){
          this.$toast.info('Over '+this.edgeLimit+' edge limit');
        }
      },
      size: function(){
        this.$toast.success('Updating Results...');
        setTimeout(()=>{
          this.$store.dispatch('handleQuery');
          this.$store.dispatch('buildURL');
        }, 1000);
      },
      ara: function(){
        this.$toast.success('Updating Results...');
        setTimeout(()=>{
          this.$store.dispatch('handleQuery');
          this.$store.dispatch('buildURL');
        }, 1000);
      },
      kp: function(){
        this.$toast.success('Updating Results...');
        setTimeout(()=>{
          this.$store.dispatch('handleQuery');
          this.$store.dispatch('buildURL');
        }, 1000);
      },
      kpSelected: function(){
        this.$toast.success('Updating Results...');
        setTimeout(()=>{
          this.$store.dispatch('handleQuery');
          this.$store.dispatch('buildURL');
        }, 1000);
      },
      araSelected: function(){
        this.$toast.success('Updating Results...');
        setTimeout(()=>{
          this.$store.dispatch('handleQuery');
          this.$store.dispatch('buildURL');
        }, 1000);
      },
      generalMode: function(){
        this.reset();
      },
    },
    methods: {
      readableName(text){
          const result = text.replace(/([A-Z])/g, " $1");
          return result.charAt(0).toUpperCase() + result.slice(1);
      },
      clear(){
        this.$store.commit('setTerm', '');
        this.search();
      },
      search(){
        this.$store.dispatch('handleQuery');
        this.$store.dispatch('buildURL');
      },
      setNodeMode(v){
        // this.generalMode = v;
        this.$store.commit('setMode', v);
      },
      numberWithCommas(x) {
          return x.toString().replace(/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g, ",");
      },
      reset() {
        let self = this;
        this.$toast.success('Resetting please wait...');
        setTimeout(function(){
          self.$store.commit('reset');
          self.$store.dispatch('handleQuery')
        }, 300);  
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
        let edgeName = item['api']['name'] + ' : ' + item['predicate'];
        this.$store.dispatch('unhighlightRow', {unhighlight: edgeName, item: item})
      },
      recenterGraph() {
        this.$store.dispatch('recenterGraph')
      },
      checkForQuery(){
          let current_url = window.location.href
          let url = new URL(current_url);
          this.$store.dispatch('handleParams', {params: url.search.slice(1)});
      }
    },
    mounted: function () {
      this.$store.dispatch('getOptions');
      this.checkForQuery();
    }
}
</script>

<style>
  summary::marker{
    color: rgb(24, 228, 255);
  }
  .query-input{
    background-color: azure;
    padding: 10px;
    border-radius: 5px;
    margin: 10px;
    border: none;
    min-width: 400px;
  }
  .tab-not-active{
    /* Permalink - use to edit and share this gradient: https://colorzilla.com/gradient-editor/#bdbdbd+1,bdbdbd+100&0.65+0,0+100 */
    background: -moz-linear-gradient(top,  rgba(189,189,189,0.65) 0%, rgba(189,189,189,0.64) 1%, rgba(189,189,189,0) 100%); /* FF3.6-15 */
    background: -webkit-linear-gradient(top,  rgba(189,189,189,0.65) 0%,rgba(189,189,189,0.64) 1%,rgba(189,189,189,0) 100%); /* Chrome10-25,Safari5.1-6 */
    background: linear-gradient(to bottom,  rgba(189,189,189,0.65) 0%,rgba(189,189,189,0.64) 1%,rgba(189,189,189,0) 100%); /* W3C, IE10+, FF16+, Chrome26+, Opera12+, Safari7+ */
    filter: progid:DXImageTransform.Microsoft.gradient( startColorstr='#a6bdbdbd', endColorstr='#00bdbdbd',GradientType=0 ); /* IE6-9 */

  }
  .edge-summary:hover{
    background-color: #f5eefd !important;
  }
  .edge-table tr:nth-child(odd){
    background-color: #e7e7e7;
  }
  .p-0{
    padding: 0;
  }
  .p-small{
    padding: 2px;
  }
  .p-1{
    padding: .5em;
  }
  .p-2{
    padding: 1em;
  }
  .p-3{
    padding: 2em;
  }
  .p-0{
    padding: 0px !important;
  }
  .border-b{
    border-bottom: solid 1px rgb(71, 13, 69);
  }
  .top-br{
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
  }
  .size-select{
    width: 80px;
    height: 30px;
    padding: 2px;
    margin: 0px 5px;
    border-radius: 10px;
  }
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
    width: 70vw;
    height: 700px;
    display: block;
    border: 2px #dddddd solid;
    background-color:white;
    overflow: hidden;
    margin: auto;
  }
  .graph-btn-container{
    position: absolute;
    right: 6vw;
    top: 10px;
    z-index: 100;
  }
  .operations-menu{
    max-height: 800px;
    overflow-y: scroll;
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