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
      Gene: '#0072B2', // blue
      Disease: '#D55E00', // vermillion
      Plant: '#009E73', // bluish green
      GrossAnatomicalStructure: '#E69F00', // orange
      Polypeptide: '#56B4E9', // sky blue
      AnatomicalEntity: '#F0E442', // yellow
      PathologicalProcess: '#CC79A7', // pink
      Procedure: '#737373', // dark gray
      DiseaseOrPhenotypicFeature: '#262626', // dark gray
      Cell: '#5A5A5A', // medium gray
      SmallMolecule: '#dd5181', // pink
      PhysiologicalProcess: '#F8766D', // salmon
      Device: '#DE8F05', // dark yellow
      CellularComponent: '#60BD68', // green
      PhenotypicFeature: '#B2912F', // brown
      MolecularActivity: '#00B0F6', // light blue
      Virus: '#FF00FF', // magenta
      Bacterium: '#9E0059', // raspberry
      Cohort: '#FB9A99', // pale red
      Fungus: '#800080', // purple
      OrganismAttribute: '#CAB2D6', // lavender
      ChemicalEntity: '#E6AB02', // mustard
      Food: '#F58231', // tangerine
      Pathway: '#B15928', // cinnamon
      OrganismTaxon: '#000000', // black
      Protein: '#CC99FF', // lavender pink
      MolecularMixture: '#66CC00', // apple green
      NucleicAcidEntity: '#FFC0CB', // pink
      Behavior: '#FFD8B1', // light peach
      Organism: '#B15928', // white
      MolecularEntity: '#CCEEFF', // baby blue
      Drug: '#1CE6FF', // neon blue
      CellLine: '#FF34FF', // hot pink
      Phenomenon: '#FFD8B1', // light peach (repeated for consistency)
      ClinicalAttribute: '#4DFF4D', // mint green
      BiologicalProcess: '#F0E442', // yellow (repeated for consistency)
      PairwiseGeneToGeneInteraction: '#B45F06', // burnt sienna
      ClinicalFinding: '#3CB44B', // green
      Activity: '#4363D8', // cerulean
      DiagnosticAid: '#E6194B', // cherry red
      Nutrient: '#800000', // maroon
      NamedThing: '#A9A9A9', // dark gray
      ClinicalIntervention: '#808080', // gray
      InformationContentEntity: '#E6194B',
      ChemicalExposure: '#000075', // navy blue
      EnvironmentalExposure: '#000000', // black (repeated for consistency)
      BiologicalEntity: '#A9A9A9', // dark gray (repeated for consistency)
      Event: '#D3D3D3', // light gray
      Publication: '#FF6347', // tomato
      GeneFamily: '#E6E600', // bright yellow
      SequenceVariant: '#1F75FE', // true blue
      ChemicalMixture: '#FF00FF', // magenta (repeated for consistency)
      Treatment: '#B15928',
      ComplexMolecularMixture: '#FFD8B1', // light peach (repeated for consistency)
      ProteinFamily: '#A9A9A9', // dark gray (repeated for consistency)
      GeneticInheritance: '#000000', // black (repeated for consistency)
      Transcript: '#696969', // dim gray
      RNAProduct: '#B15928',
      Agent: '#A9A9A9', // dark gray (repeated for consistency)
      MaterialSample: '#FF7F00', // orange
      LifeStage: '#000000', // black (repeated for consistency)
      MicroRNA: '#B15928',
      OrganismalEntity: '#A9A9A9', // dark gray (repeated for consistency)
      NoncodingRNAProduct: '#000000', // black (repeated for consistency)
      BehavioralFeature: '#B15928',
      PopulationOfIndividualOrganisms: '#A9A9A9', // dark gray (repeated for consistency)
      IndividualOrganism: '#000000', // black (repeated for consistency)
      BiologicalProcessOrActivity: '#B15928'
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
