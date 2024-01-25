import axios from 'axios';

export const registry = {
  state: () => ({
    tags: [],
    authors: [],
    // key is the direct field to be filtered by
    //value is the final val set to ES
    all_filters: {
      'info.x-translator.component': [],
      'info.x-trapi.version': [],
      'tags.name': []
    },
    entityColors: {
      Gene: '#3f84bb',
      Disease: '#8d5bd4',
      Plant: '#087a3c',
      GrossAnatomicalStructure: 'coral',
      Polypeptide: '#07566f',
      AnatomicalEntity: '#d65042',
      PathologicalProcess: '#262071',
      Procedure: '#683682',
      DiseaseOrPhenotypicFeature: '#8d5bd4',
      Cell: '#ff6e54',
      SmallMolecule: '#e91e62',
      PhysiologicalProcess: '#07566f',
      Device: '#25282a',
      CellularComponent: '#224b80',
      PhenotypicFeature: '#369ac1',
      MolecularActivity: '#d65042',
      Virus: '#642d87',
      Bacterium: '#3684af',
      Cohort: '#b5cb17',
      Fungus: '#ff6e54',
      OrganismAttribute: '#5046e4',
      ChemicalEntity: 'orange',
      Food: 'pink',
      Pathway: 'teal',
      OrganismTaxon: 'red',
      Protein: 'lightblue',
      MolecularMixture: 'hotpink',
      NucleicAcidEntity: 'black',
      Behavior: 'purple',
      Organism: 'limegreen',
      MolecularEntity: 'green',
      Drug: '#fab670',
      Drug: '#fab670',
      CellLine: '#02838f',
      Phenomenon: 'yellow',
      ClinicalAttribute: '#a50202',
      BiologicalProcess: '#b5cb17',
      PairwiseGeneToGeneInteraction: '#444e86',
      ClinicalFinding: 'brown'
    }
  }),
  mutations: {
    saveFilters(state, payload) {
      state[payload['type']] = payload['value'];
    },
    saveAllFilters(state, payload) {
      if (payload['type'] == 'tags.name') {
        state.all_filters[payload['type']].push(payload['value'][0]);
      } else {
        state.all_filters[payload['type']] = payload['value'];
      }
    }
  },
  actions: {
    loadTagFilters({ commit }) {
      const existing = sessionStorage.getItem('tags');
      if (!existing) {
        let tagUrl =
          process.env.NODE_ENV == 'development'
            ? 'https://smart-api.info' + '/api/suggestion?field=tags.name'
            : '/api/suggestion?field=tags.name';
        axios.get(tagUrl).then(function (response) {
          let temp_data = [];
          for (let key in response.data) {
            temp_data.push({ key: key, doc_count: response.data[key] });
          }
          let tags = temp_data.map((item) => {
            return { name: item.key, count: item.doc_count, active: false };
          });
          commit('saveFilters', { type: 'tags', value: tags });
          //save to sessionStorage
          sessionStorage.setItem('tags', JSON.stringify(tags));
        });
      } else {
        commit('saveFilters', { type: 'tags', value: JSON.parse(existing) });
      }
    },
    loadOwnerFilters({ commit }) {
      const existing = sessionStorage.getItem('authors');
      if (!existing) {
        let ownerUrl =
          process.env.NODE_ENV == 'development'
            ? 'https://smart-api.info' + '/api/suggestion?field=info.contact.name'
            : '/api/suggestion?field=info.contact.name';
        axios.get(ownerUrl).then(function (response) {
          let temp_data = [];
          for (let key in response.data) {
            temp_data.push({ key: key, doc_count: response.data[key] });
          }
          let authors = temp_data.map((item) => {
            return { name: item.key, count: item.doc_count, active: false };
          });
          commit('saveFilters', { type: 'authors', value: authors });
          //save to sessionStorage
          sessionStorage.setItem('authors', JSON.stringify(authors));
        });
      } else {
        commit('saveFilters', { type: 'authors', value: JSON.parse(existing) });
      }
    },
    aggregate({ commit }, field) {
      const existing = sessionStorage.getItem(field);
      if (!existing) {
        let url =
          process.env.NODE_ENV == 'development'
            ? `https://dev.smart-api.info/api/suggestion?field=${field}`
            : `/api/suggestion?field=${field}`;
        axios
          .get(url)
          .then((response) => {
            let complete = [];
            let res = response.data || [];
            for (const [key, value] of Object.entries(res)) {
              let item = {};
              item.color = field.includes('trapi') ? '#f06292' : '#303f9f';
              item.active = false;
              item.value = key;
              item.name = key;
              item.count = value;
              item.es_value = field + ':' + key;

              complete.push(item);
            }
            commit('saveAllFilters', { type: field, value: complete });
            sessionStorage.setItem(field, JSON.stringify(complete));
          })
          .catch((err) => {
            throw err;
          });
      } else {
        commit('saveAllFilters', { type: field, value: JSON.parse(sessionStorage.getItem(field)) });
      }
    },
    loadTranslatorFilters({ dispatch, commit }) {
      dispatch('aggregate', 'info.x-translator.component');
      //set here to preserve desired order
      [
        {
          query: '/api/query?q=tags.name:translator&tags=%22biothings%22&size=0',
          name: 'BioThings',
          type: 'tags.name',
          value: 'biothings',
          es_value: 'tags.name:biothings'
        },
        {
          query: '/api/query?q=tags.name:translator&tags=%22trapi%22&size=0',
          name: 'TRAPI',
          type: 'tags.name',
          value: 'trapi',
          es_value: 'tags.name:trapi'
        },
        //special NOT includes multiple values
        {
          query:
            '/api/query?q=!tags.name:biothings AND !tags.name:trapi&tags=%22translator%22&size=0',
          name: 'Other',
          type: '!tags.name',
          value: 'trapi AND !tags.name:biothings',
          es_value: '(!tags.name:trapi AND !tags.name:biothings)'
        }
      ].forEach((item) => {
        let url =
          process.env.NODE_ENV == 'development'
            ? 'https://dev.smart-api.info' + item.query
            : item.query;
        axios.get(url).then(function (response) {
          commit('saveAllFilters', {
            type: item.type,
            value: [
              {
                name: item.name,
                value: item.value,
                active: false,
                color: '#424242',
                count: response.data?.total || false,
                es_value: item.es_value
              }
            ]
          });
        });
      });

      dispatch('aggregate', 'info.x-trapi.version.raw');
    }
  },
  getters: {
    tags: (state) => {
      return state.tags;
    },
    authors: (state) => {
      return state.authors;
    },
    all_filters: (state) => {
      return state.all_filters;
    },
    getEntityColor: (state) => (name) => {
      // function getRandomColor() {
      //   var letters = "0123456789ABCDEF";
      //   var color = "#";
      //   for (var i = 0; i < 6; i++) {
      //     color += letters[Math.floor(Math.random() * 16)];
      //   }
      //   return color;
      // }
      if (name in state.entityColors) {
        return state.entityColors[name];
      } else {
        return '#9c27b0';
      }
    }
  }
};
