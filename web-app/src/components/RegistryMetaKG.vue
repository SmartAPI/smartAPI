<template>
  <div class="grey lighten-2 metakg-card p-0 m-0 row">
    <h3 class="p-2 purple-text" v-if="loading">Loading...</h3>
    <template v-if="!loading && !noHits">
      <div class="col s12 m8">
        <h5 style="font-weight: lighter">
          MetaKG Entity Overview
          <small class="right"
            >Edges ({{ numberWithCommas(total) }}) | Objects ({{ objects.length }}) | Subjects ({{
              subjects.length
            }})</small
          >
        </h5>
        <p v-if="total && total > size" class="center yellow lighten-4 orange-text rounded">
          This is just a subset of the available MetaKG ({{ numberWithCommas(size) }}/{{
            numberWithCommas(total)
          }})
        </p>
        <div
          v-if="graphData"
          class="hide-on-small-only"
          style="max-height: 500px; overflow-y: scroll"
        >
          <div class="d-flex flex-wrap align-items-start">
            <template v-for="(subjects, object) in graphData" :key="object">
              <EntityPill :object="object" :subjects="subjects"></EntityPill>
            </template>
          </div>
        </div>
      </div>
      <div class="col s12 m4 grey darken-4">
        <div class="d-flex justify-content-center">
          <img class="scale-in-center" src="@/assets/img/metakg-01.png" width="80" />
          <h5 class="white-text center" style="font-weight: lighter">MetaKG Explorer</h5>
        </div>
        <template v-if="networkData">
          <SimpleNetwork :nodes="networkData.nodes" :edges="networkData.edges"></SimpleNetwork>
        </template>
        <p v-if="total && total > size" class="center yellow lighten-2 black-text rounded">
          This is just a subset of the available MetaKG ({{ numberWithCommas(size) }}/{{
            numberWithCommas(total)
          }})
        </p>
        <p class="center">
          <span class="white-text caps">
            Explore <b>the full</b> {{ api.info.title }}'s MetaKG
          </span>
        </p>
        <div class="d-flex justify-content-center align-items-center p-1">
          <router-link
            class="btn btn-large purple white-text"
            target="_blank"
            :to="{
              path: '/portal/translator/metakg',
              query: {
                q: 'api.smartapi.id:' + api._id
              }
            }"
            >Try It Now <i class="fa fa-external-link" aria-hidden="true"></i
          ></router-link>
        </div>
        <p class="center hide-on-med-and-up">
          <span class="yellow-text caps"> Not recommended for use on small screens </span>
        </p>
      </div>
    </template>
    <div v-if="!loading && noHits">
      <p class="center grey-text p-2">Oops...Can't load this right now...</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

import EntityPill from './EntityPill.vue';
import SimpleNetwork from './SimpleNetworkCosmo.vue';

export default {
  name: 'RegistryMetaKG',
  components: {
    EntityPill,
    SimpleNetwork
  },
  props: {
    api: {
      type: Object,
      default: {}
    }
  },
  data: function () {
    return {
      loading: true,
      graphData: null,
      networkData: null,
      noHits: false,
      total: 0,
      size: 5000,
      objects: [],
      subjects: []
    };
  },
  watch: {
    // open: function (v) {
    //   if (v) {
    //     if (!this.graphData) {
    //       this.sendRequest();
    //     }
    //   }
    // }
  },
  mounted: function () {
    if (!this.graphData) {
      this.sendRequest();
    }
  },
  methods: {
    numberWithCommas(x) {
      return x.toString().replace(/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g, ',');
    },
    getNetworkData(hits) {
      let self = this;
      let nodes = new Set();
      let edges = [];
      let nodeData = [];
      let nodeWeight = {};

      hits.forEach((hit) => {
        if (hit.object in nodeWeight) {
          nodeWeight[hit.object] += 1;
        } else {
          nodeWeight[hit.object] = 1;
        }
        if (hit.subject in nodeWeight) {
          nodeWeight[hit.subject] += 1;
        } else {
          nodeWeight[hit.subject] = 1;
        }
        nodes.add(hit.object);
        nodes.add(hit.subject);
        edges.push({
          // group: 'edges',
          // data: {
          id: Math.floor(100000 + Math.random() * 900000),
          source: hit.subject,
          target: hit.object
          // }
        });
      });

      nodeData = [...nodes].map((node) => {
        return {
          // group: 'nodes',
          // data: {
          weight: nodeWeight[node] + 100,
          id: node,
          name: node[0],
          color: self.$store.getters.getEntityColor(node)
          // }
        };
      });
      this.networkData = {
        nodes: nodeData,
        edges: edges
      };
    },
    getFacetData(facets) {
      if (facets?.['object.raw']?.terms) {
        this.objects = facets?.['object.raw']?.terms.map((v) => v.term);
      }
      if (facets?.['subject.raw']?.terms) {
        this.subjects = facets?.['subject.raw']?.terms.map((v) => v.term);
      }
    },
    sendRequest() {
      let self = this;
      let base = process.env.NODE_ENV == 'development' ? 'https://dev.smart-api.info' : '';
      axios
        .get(
          base +
            '/api/metakg?q=(api.name:"' +
            self.api.info.title +
            '")&size=' +
            self.size +
            '&fields=object,subject&facet_size=300&aggs=object.raw,subject.raw'
        )
        .then((res) => {
          let data = {};
          if (res.data?.hits && res.data?.hits?.length) {
            self.total = res.data?.total;
            self.getNetworkData(res.data.hits);
            self.getFacetData(res.data?.facets);
            res.data.hits.forEach((item) => {
              if (!(item.subject in data)) {
                data[item.subject] = [item.object];
              } else {
                if (item.subject in data && !data[item.subject].includes(item.object)) {
                  data[item.subject].push(item.object);
                }
              }
            });
            let sortable = [];
            for (var key in data) {
              sortable.push([key, data[key]]);
            }
            sortable.sort(function (a, b) {
              return a[1].length - b[1].length;
            });
            sortable.reverse();
            let objSorted = {};
            sortable.forEach(function (item) {
              objSorted[item[0]] = item[1].sort();
            });
            data = objSorted;

            self.graphData = data;
            self.loading = false;
            self.noHits = false;
          } else {
            self.noHits = true;
            self.loading = false;
          }
        })
        .catch((err) => {
          self.loading = false;
          self.noHits = true;
          throw err;
        });
    }
  }
};
</script>
