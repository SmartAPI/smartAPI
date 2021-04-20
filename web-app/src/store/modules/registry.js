import axios from 'axios'

export const registry = {
    state: () => ({ 
        tags:[],
        authors: [],
        // key is the direct field to be filtered by
        //value is the final val set to ES
        all_filters: {
            'info.x-translator.component':[],
            'info.x-trapi.version':[],
            'tags.name':[]
        }
    }),
    mutations: {
        saveFilters(state, payload){
            state[payload['type']] = payload['value']
        },
        saveAllFilters(state, payload){
            if (payload['type'] == 'tags.name') {
                state.all_filters[payload['type']].push(payload['value'][0])
            }else{
                state.all_filters[payload['type']] = payload['value']
            }
        },
    },
    actions: {
        loadTagFilters({ commit }){
            const existing = sessionStorage.getItem('tags');
            if(!existing){
                let tagUrl = window.location.hostname !== 'localhost' ? "/api/suggestion?field=tags.name" : 'https://smart-api.info/api/suggestion?field=tags.name'
                axios.get(tagUrl).then(function(response){
                    let temp_data = []
                    for(let key in response.data){
                        temp_data.push({key: key, doc_count: response.data[key]})
                    }
                    let tags = temp_data.map(item => { return { name: item.key, 'count': item.doc_count, active: false} })
                    commit('saveFilters', {type: 'tags', value: tags})
                    //save to sessionStorage
                    sessionStorage.setItem('tags',JSON.stringify(tags));
                });
            }else{
                commit('saveFilters', {type: 'tags', value: JSON.parse(existing)})
            }
            
        },
        loadOwnerFilters({ commit }){
            const existing = sessionStorage.getItem('authors');
            if(!existing){
                let ownerUrl = window.location.hostname !== 'localhost' ? "/api/suggestion?field=info.contact.name" : 'https://smart-api.info/api/suggestion?field=info.contact.name'
                axios.get(ownerUrl).then(function(response){
                    let temp_data = []
                    for(let key in response.data){
                        temp_data.push({key: key, doc_count: response.data[key]})
                    }
                    let authors = temp_data.map(item => { return { name: item.key, 'count': item.doc_count, active: false} })
                    commit('saveFilters', {type: 'authors', value: authors})
                    //save to sessionStorage
                    sessionStorage.setItem('authors',JSON.stringify(authors));
                });
            }else{
                commit('saveFilters', {type: 'authors', value: JSON.parse(existing)})
            }
            
        },
        aggregate({commit}, field){
            const existing = sessionStorage.getItem(field);
            if(!existing){
                let url = window.location.hostname !== 'localhost' ? `/api/suggestion?field=${field}` : `https://smart-api.info/api/suggestion?field=${field}`
                axios.get(url).then(response => {
                    let complete = []
                    let res = response.data || []
                    for (const [key, value] of Object.entries(res)) {
                        let item = {}
                        item.color = field.includes('trapi') ? '#f06292': '#303f9f'
                        item.active = false
                        item.value = key
                        item.name = key
                        item.count = value
                        complete.push(item)
                    }
                    commit('saveAllFilters', {type: field, value: complete});
                    sessionStorage.setItem(field, JSON.stringify(complete));
                }).catch(err=>{
                    throw err;
                });
            }else{
                commit('saveAllFilters', {type: field, value: JSON.parse(sessionStorage.getItem(field))});
            }
        },
        loadTranslatorFilters({dispatch, commit}){
            dispatch('aggregate', 'info.x-translator.component');
            //set here to preserve desired order
            let bturl = window.location.hostname !== 'localhost' ? "/api/query?q=tags.name:biothings AND tags.name:translator&size=0" 
            : 'https://smart-api.info/api/query?q=tags.name:biothings AND tags.name:translator&size=0'
            axios.get(bturl).then(function(response){
                commit('saveAllFilters', {
                    type: 'tags.name', 
                    value: [
                        { 
                            name:'BioThings', 
                            value:'biothings',
                            active:false, 
                            color: '#424242', 
                            count: response.data?.total || false
                        }
                    ]
                })
            });

            let trapiurl = window.location.hostname !== 'localhost' ? "/api/query?q=tags.name:trapi AND tags.name:translator&size=0" 
            : 'https://smart-api.info/api/query?q=tags.name:trapi AND tags.name:translator&size=0'
            axios.get(trapiurl).then(function(response){
                commit('saveAllFilters', {
                    type: 'tags.name', 
                    value: [
                        {
                            name:'TRAPI',
                            value:'trapi',
                            active:false,
                            color: '#424242',
                            count: response.data?.total || false
                        }
                    ]
                })
            });

            //special NOT includes multiple values
            let otherurl = window.location.hostname !== 'localhost' ? "/api/query?q=!tags.name:trapi AND tags.name:translator AND !tags.name:biothings&size=0" 
            : 'https://smart-api.info/api/query?q=!tags.name:trapi AND tags.name:translator AND !tags.name:biothings&size=0'
            axios.get(otherurl).then(function(response){
                commit('saveAllFilters', {
                    type: '!tags.name', 
                    value: [
                        {name:'Other',
                        value:'trapi AND !tags.name:biothings',
                        active:false,
                        color: '#424242',
                        count: response.data?.total || false
                    }
                    ]
                })
            });
            
            dispatch('aggregate', 'info.x-trapi.version')
        }
    },
    getters: {
        tags: (state) => {
            return state.tags
        },
        authors: (state) => {
            return state.authors
        },
        all_filters: (state) => {
            return state.all_filters
        },
    }
}