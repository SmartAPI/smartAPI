<template>
  <div class="p-1">
    <p class="orange-text m-0" style="padding-bottom: 10px">
      View biomedical entity knowledge available
      <button @click="open = !open" type="button" class="clearButtonSmall">
        {{ open ? 'CLOSE' : 'OPEN' }}
      </button>
    </p>
    <div v-if="open" class="grey lighten-2 metakg-card p-0 row d-flex align-items-stretch">
      <h3 class="p-2 grey-text" v-if="loading">Loading...</h3>
      <template v-if="!loading && !noHits">
        <div class="col s12 m8">
          <h5 style="font-weight: lighter">Entity Relationship Overview</h5>
          <div v-if="graphData" style="max-height: 500px; overflow-y: scroll">
            <div class="d-flex flex-wrap align-items-start">
              <template v-for="(subjects, object) in graphData" :key="object">
                <EntityPill :object="object" :subjects="subjects"></EntityPill>
              </template>
            </div>
          </div>
        </div>
        <div class="col s12 m4 grey darken-3">
          <div class="d-flex justify-content-center">
            <img class="scale-in-center" src="@/assets/img/metakg-01.png" width="80" />
            <h5 class="white-text center" style="font-weight: lighter">MetaKG Explorer</h5>
          </div>
          <template v-if="networkData">
            <SimpleNetwork :nodes="networkData.nodes" :edges="networkData.edges"></SimpleNetwork>
          </template>
          <p class="center">
            <span class="white-text caps"> Explore {{ api.info.title }}'s MetaKG </span>
          </p>
          <div class="d-flex justify-content-center align-items-center p-1">
            <router-link
              class="btn btn-large purple white-text"
              target="_blank"
              :to="{
                path: '/portal/translator/metakg',
                query: {
                  'api.x-translator.component': api?.info?.['x-translator']?.component,
                  'api.name': api.info.title
                }
              }"
              >Try It Now</router-link
            >
          </div>
        </div>
      </template>
      <div v-if="!loading && noHits">
        <p class="center grey-text p-2">Oops...Can't load this right now...</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

import EntityPill from './EntityPill.vue';
import SimpleNetwork from './SimpleNetwork.vue';

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
      open: false,
      loading: true,
      graphData: null,
      networkData: null,
      noHits: false
    };
  },
  watch: {
    open: function (v) {
      if (v) {
        if (!this.graphData) {
          this.sendRequest();
        }
      }
    }
  },
  methods: {
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
          group: 'edges',
          data: {
            id: Math.floor(100000 + Math.random() * 900000),
            source: hit.subject,
            target: hit.object
          }
        });
      });

      nodeData = [...nodes].map((node) => {
        return {
          group: 'nodes',
          data: {
            weight: nodeWeight[node] + 100,
            id: node,
            color: self.$store.getters.getEntityColor(node)
          }
        };
      });
      this.networkData = {
        nodes: nodeData,
        edges: edges
      };
    },
    sendRequest() {
      let self = this;
      let base = process.env.NODE_ENV == 'development' ? 'https://dev.smart-api.info' : '';
      axios
        .get(
          base +
            '/api/metakg?size=20&q=(api.name:"' +
            self.api.info.title +
            '")&size=300&fields=object,subject'
        )
        .then((res) => {
          let data = {};
          if (res.data?.hits && res.data?.hits?.length) {
            self.getNetworkData(res.data.hits);
            res.data.hits.forEach((item) => {
              if (!(item.subject in data)) {
                data[item.subject] = [item.object];
              } else {
                if (item.subject in data && !data[item.subject].includes(item.object)) {
                  data[item.subject].push(item.object);
                }
              }
            });
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
