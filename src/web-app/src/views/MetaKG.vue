<template>
  <main id="meta-app" class="white" style="width: 100%;" v-cloak>
  <div class="loadBlock row" v-if="loading && !apisProcessed">
    <div class="col s12 m2 center d-flex align-items-center">
      <i class="fa fa-cog fa-spin fa-fw fa-3x"></i>
    </div>
    <div class="col s12 m10 center">
      <h6 class="grey-text">
        This process might take several seconds.
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
      <h3>
        <img />
          <Image class="scale-in-center" img_name="metakg-01.png" img_width="50px"
          style="max-width: 50px; max-height: 50px;" ></Image>
        Meta-KG
      </h3>
      <p>
        Search for API operations given a combination of input, output(s),
        and/or predicates.
      </p>
      <p>
        An <a href="#" @click.prevent="loadExample()">example</a> would be: all
        operations where the predicate is "treats" and its output is a
        "Disease".
      </p>
      <p style="text-align: right;">
        <a href="https://smart-api.info/api/metakg" target="_blank" rel="noreferrer"><small>Download
            Meta-KG dump</small></a>
      </p>
    </div>
    <hr />
    <!-- META KG SEARCH -->
    <div class="row">
      <div class="col s12">
        <form class="meta_kg_form">
          <div class="row">
            <div class="col s12 m4 input-field center">
              <h5 class="white-text">
                <i class="fa fa-sign-in black-text" aria-hidden="true"></i>
                INPUT TYPE
              </h5>
              <div class="center white-text">
                <small>(1 or Many)</small>
              </div>
              <PillBox type="input_type"></PillBox>
            </div>
            <div class="col s12 m4 input-field center">
              <h5 class="white-text">
                <i class="fa fa-connectdevelop purple-text" aria-hidden="true"></i>
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
            <div class="col s12 center">
              <button v-if="!loading" class="btn red" type="button" @click.prevent="reset()">
                Clear
              </button>
            </div>
          </div>
        </form>
      </div>
      <div class="col s12 m4">
        <div v-show="results && results.length" class="collection-item red-text" style="padding: 1px;">
          <small v-text="results.length+' operations'"></small>
        </div>
        <div class="white padding20 resBox collection">
          <template v-show="results && results.length">
            <div class="collection-item row" style="padding: 2px;">
              <div class="col s3">
                <small>API</small>
              </div>
              <div class="col s9">
                <small>Relationship</small>
              </div>
            </div>
          </template>
          <template v-for="item in results" :key="item.association.smartapi.id">
            <div class="collection-item resultRow row" @mouseenter="highlightRow(item)"
              @mouseleave="unhighlightRow(item)" style="padding: 3px;">
              <div class="col s12 left">
                <small class="d-block">
                  <a target="_blank" rel="noreferrer" :href="'/registry?q='+item.association.smartapi.id">
                    <b v-text="item.association.api_name"></b>
                    <i @mouseenter="highlightRowAndZoom(item)" @mouseleave="recenterGraph()"
                      class="fa fa-search-plus pointer blue-grey-text" aria-hidden="true"></i>
                  </a>
                  <i class="fa fa-info-circle resultInfo pointer green-text" aria-hidden="true"
                    style="float: right;"></i>
                </small>
                <small class="s-badge lighten-4 grey-text" v-text="item.association.input_type"></small>
                <small class="blue-text">/</small>
                <small class="s-badge lighten-5 purple-text" v-text="item.association.predicate"></small>
                <small class="blue-text">/</small>
                <small class="s-badge lighten-5 orange-text" v-text="item.association.output_type"></small>
              </div>
            </div>
          </template>
          <template v-if="results.length == 0 && !loading">
            <small class="grey-text">No Results</small>
          </template>
        </div>
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
          <small>Results contain over <b v-text="edgeLimit"></b> edges, please refine your query to see edges rendered.</small>
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
import ClipboardJS from "clipboard"
import tippy from 'tippy.js';
import axios from 'axios'

import Image from '../components/Image.vue';
import PillBox from '../components/PillBox.vue';

const kg = require("@biothings-explorer/smartapi-kg")

export default {
  components: { 
      Image,
      PillBox
  },
    name: 'MetaKG',
    data: function () {
      return {
        'cy': null,
        'showAPIS': false,
        'showTags': false,
        'apisProcessed': false,
        'apisLoaded': false,
        'totalApis': 0,
        'hoverInfo': {}
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
      loading: function (isLoading) {
        if (!isLoading) {
          //when done loading check URL for existing extra_params
          let finalURL = window.location.href
          let url = new URL(finalURL);

          var payload = {};
          payload["params"] = url.search.slice(1);
          this.$store.dispatch('handleParams', payload);
        }
      },
      results: function () {
        var self = this;
        setTimeout(function () {
          self.createTips();
        }, 1000);
      }
    },
    methods: {
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

        let meta_kg = new kg();
        //load meta-kg API graph with reasoner APIs
        const t0 = performance.now();
        /*eslint-disable */
        await meta_kg.constructMetaKG();
        /*eslint-enable */
        const t1 = performance.now();
        self.apisLoaded = true;
        //performance check
        var seconds = (((t1 - t0) % 60000) / 1000).toFixed(0);
        console.log(`%c Getting Meta-KG graph took ${seconds} seconds.`, 'color:limegreen');

        //send graph data to store for processing
        this.$store.commit('loadMetaKG', {'graph': meta_kg});
        this.$store.commit('drawGraph');
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
        this.$store.commit('reset');
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

      },
      recenterGraph() {
        this.$store.dispatch('recenterGraph')
      },
      checkforQuery: function () {
        var self = this;
        var url_string = window.location.href
        var url = new URL(url_string);

        var q = url.searchParams.get("q");
        if (q) {
          this.query = q;
        }

        var tags = url.searchParams.get("tags");
        if (tags) {
          if (tags.includes(',')) {
            tags = tags.split(',')
          } else {
            tags = [tags]
          }
          for (var i = 0; i < tags.length; i++) {
            for (var x = 0; x < self.tags.length; x++) {
              if (self.tags[x].name === tags[i]) {
                var payload = {};
                payload["tag"] = self.tags[x];
                this.$store.commit('toggleTag', payload);
              }
            }
          }
        }

        var owners = url.searchParams.get("owners");
        if (owners) {
          if (owners.includes(',')) {
            owners = owners.split(',')
          } else {
            owners = [owners]
          }
          for (var ii = 0; ii < owners.length; ii++) {
            for (var xx = 0; xx < self.authors.length; xx++) {
              if (self.authors[xx].name === owners[ii]) {
                var payload2 = {};
                payload2["author"] = self.authors[xx];
                this.$store.commit('toggleAuthor', payload2);
              }
            }
          }
        }

      },
      copy() {
        this.$swal.fire({
          type: 'success',
          toast: true,
          title: 'Copied',
          showConfirmButton: false,
          timer: 1000
        });
      },
      createTips() {
        var self = this;

        tippy(".resultInfo", {
          trigger: 'click',
          placement: 'top-start',
          interactive: true,
          animation: 'fade',
          theme: 'light',
          onShow(instance) {
            if (self.hoverInfo) {
              // hover item info saved to state
              let info = self.hoverInfo
              let desc = ""
              let status = "N/A"

              axios.get("/api/query?size=1&q=_id:"+info.association.smartapi.id+"&fields=info.description,_meta.uptime_status").then(res=>{
                // console.log(res.data);

                if (res.data.hits.length) {
                  desc = res.data.hits[0]['info']['description'].substring(0,400)+'...';
                  if (res.data.hits[0] && res.data.hits[0]['_status'] && res.data.hits[0]['_status']["uptime_status"]) {
                    status = res.data.hits[0]['_status']['uptime_status']
                  }else{
                    status = "N/A"
                  }

                  instance.setContent(`<div>
                  <h6>API: <a target="_blank" href="/registry?q=` + info.association.smartapi.id + `">` + info
                  .association.api_name + `</a></h6>
                  <p><small>`+desc+`<a target="_blank" href="/registry?q=` + info.association.smartapi.id + `">Learn More</a></small></p>
                  <b><small>API Status: `+status+`</small></b>
                  <table>
                    <tbody>
                      <tr class="grey lighten-4">
                        <td>
                          <small class="grey-text">INPUT/ID TYPE</small>
                        </td>
                        <td>
                          <small>` + info.association.input_type + `/` + info.association.input_id + `</small>
                        </td>
                      </tr>
                      <tr class="purple lighten-4">
                        <td>
                          <small class="purple-text">RELATIONSHIP</small>
                        </td>
                        <td>
                          <small>` + info.association.predicate + `</small>
                        </td>
                      </tr>
                      <tr class="orange lighten-4">
                        <td>
                          <small class="orange-text">OUTPUT/ID TYPE</small>
                        </td>
                        <td>
                          <small>` + info.association.output_type + `/` + info.association.output_id + `</small>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                  </div>`)
                }else{
                  instance.setContent(`<div>No details were found on SmartAPI</div>`)
                }

              }).catch(err=>{
                
                instance.setContent(`<div>
                <h6>API: <a target="_blank" href="/registry?q=` + info.association.smartapi.id + `">` + info
                .association.api_name + `</a></h6>
                <p><small>`+desc+`</small></p>
                <table>
                  <tbody>
                    <tr class="grey lighten-4">
                      <td>
                        <small class="grey-text">INPUT/ID TYPE</small>
                      </td>
                      <td>
                        <small>` + info.association.input_type + `/` + info.association.input_id + `</small>
                      </td>
                    </tr>
                    <tr class="purple lighten-4">
                      <td>
                        <small class="purple-text">RELATIONSHIP</small>
                      </td>
                      <td>
                        <small>` + info.association.predicate + `</small>
                      </td>
                    </tr>
                    <tr class="orange lighten-4">
                      <td>
                        <small class="orange-text">OUTPUT/ID TYPE</small>
                      </td>
                      <td>
                        <small>` + info.association.output_type + `/` + info.association.output_id + `</small>
                      </td>
                    </tr>
                  </tbody>
                </table>
                </div>`);

                throw err;

              });
              
            }
          }
        });
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

      new ClipboardJS('.copyBtn');
      ClipboardJS.isSupported();

    }
}
</script>

<style>

</style>