import cytoscape from 'cytoscape'
import popper from 'cytoscape-popper';
import tippy from 'tippy.js';

export const metakg = {
    state: () => ({ 
        'name': 'translator',
        "meta_kg": null,
        "results": [],
        "output_autocomplete": [],
        "input_autocomplete": [],
        "predicate_autocomplete": [],
        "cyto_data": [],
        "output_type": [],
        "input_type": [],
        "predicate": [],
        "apis": {},
        'cy': null,
        "predicate_selected": [],
        "input_selected": [],
        "output_selected": [],
        "spread": false,
        "tagList": [],
        "operationsTotal": 0,
        "loading": false,
        "predicate_autocomplete_all": [],
        'overEdgeLimit': false,
        'showAllEdges': true,
        'maxEdgesRendered': 1000
     }),
    strict: true,
    mutations: {
        toggleLoading(state, payload) {
            state.loading = payload['loading'];
        },
        reset(state) {
        // only clear if it has something or it will trigger a search unnecessarily on other components
        if (state.predicate_selected.length) {
            state.predicate_selected = [];
        }
        if (state.input_selected.length) {
            state.input_selected = [];
        }
        if (state.output_selected.length) {
            state.output_selected = [];
        }

        state.predicate = [];
        state.input_type = [];
        state.output_type = [];
        },
        saveInput(state, payload) {

        let name = payload['name'];

        switch (name) {
            case 'output_type':
            state.output_type = payload["q"]
            break;
            case 'input_type':
            state.input_type = payload["q"]
            break;
            case 'predicate':
            state.predicate = payload["q"]
            break;
            default:
            console.log('no match')
        }
        },
        drawGraph(state) {
        const t0 = performance.now();
        var self = this;

        cytoscape.use(popper);

        this.cy = cytoscape({
            container: document.getElementById('cy'),
            elements: state.cyto_data,
            hideEdgesOnViewport: true,
            layout: {
            name: "concentric",
            avoidOverlap: true,
            avoidOverlapPadding: 200,
            minNodeSpacing: 200,
            },
            style: [
            {
                selector: 'node',
                style: {
                'content': 'data(name)',
                'min-zoomed-font-size': '2em',
                "text-valign": "bottom",
                "text-halign": "center",
                'color': '#3c5f99',
                'font-size': '3em',
                'text-outline-width': 4,
                'text-outline-color': 'white',
                'background-color': '#9c27b0',
                'z-index': 1000
                }
            },
            {
                selector: 'node:selected',
                style:{
                'background-color': 'red',
                }
            },
            {
                selector: 'edge',
                style:{
                'curve-style': 'bezier',
                'line-color': 'lightblue',
                'target-arrow-shape': 'triangle',
                'target-arrow-color': '#257FC5',
                'width': 2,
                'z-index': 1,
                }
            },
            {
                selector: 'edge:selected',
                style:{
                'z-index': 1000,
                'color': '#9c27b0',
                'font-size': '2.5em',
                'width': 4,
                'line-color': '#f24141',
                'target-arrow-color': '#f24141',
                'arrow-scale': 2
                }
            },
            {
                selector: '.highlightedTag',
                style:{
                'line-color': '#673782',
                'target-arrow-color': '#f24141',
                'width': 4,
                }
            },
            {
                selector: '.highlightedAPI',
                style:{
                'line-color': 'red',
                'target-arrow-color': '#f24141',
                'width': 4,
                }
            },
            ]
        });

        this.cy.$('node').on('grab', function (e) {
            var ele = e.target;
            ele.connectedEdges().select()
        });

        this.cy.on('mouseover', 'edge', function(evt){
            var edge = evt.target;
            edge.select()
        });

        this.cy.on('mouseout', 'edge', function(evt){
            var edge = evt.target;
            edge.deselect()
        });

        this.cy.$('node').on('free', function (e) {
            var ele = e.target;
            ele.connectedEdges().unselect()
        });
          
        function makePopper(ele) {
            let ref = ele.popperRef();
            ele.tippy = tippy(document.createElement('div'), {
            getReferenceClientRect: ref.getBoundingClientRect,
            content: ele.id(),
            hideOnClick: false,
            placement:'top-start',
            theme:'light',
            appendTo: document.body // or append dummyDomEle to document.body
            });
        }

        function makePopperEdge(ele) {
            let ref = ele.popperRef();
            ele.tippy = tippy(document.createElement('div'), {
            getReferenceClientRect: ref.getBoundingClientRect,
            content:`<div><h6 class="center">`+ele.data('api_name')+`</h6><b class="grey darken-2 badgepill">`+ele.data('source')+
            `</b> <b class="purple-text">`+ele.data('predicate')+
            `</b> <b class="orange darken-2 badgepill">`+ele.data('target')+
            `</b></div>`,
            hideOnClick: false,
            placement:'top-start',
            theme:'light',
            appendTo: document.body // or append dummyDomEle to document.body
            });
        }

        
        this.cy.ready(function () {
            self.cy.elements().forEach(function (ele) {           
            if(!ele.isNode()){
                makePopperEdge(ele);
            }else{
                makePopper(ele);
            }
            });
        });

        this.cy.elements().unbind('mouseover');
        this.cy.elements().bind('mouseover', (event) => event.target.tippy.show());

        this.cy.elements().unbind('mouseout');
        this.cy.elements().bind('mouseout', (event) => event.target.tippy.hide());

        this.cy.elements().unbind('drag');
        this.cy.elements().bind('drag', (event) => event.target.tippy.popperInstance.update());

        this.cy.maxZoom(2)

        const t1 = performance.now();
        var seconds = (((t1 - t0) % 60000) / 1000).toFixed(0);
        console.log(`%c Rendering graph took ${seconds} seconds.`, 'color:yellow');
        },
        saveContext(state, payload) {
        state.name = payload['context']['portal'];
        },
        saveCytoData(state, payload) {
        state.cyto_data = payload['data'];
        },
        saveOperations(state, payload) {
        state.operations = payload['ops'];
        },
        getNewOptions(state, payload) {
        let filteredOptions = payload['res'];
        const t0 = performance.now();
        let predicates = new Set();
        let inputs = new Set();
        let outputs = new Set();

        // PREDICATES
        if (!state.output_selected.length && !state.input_selected.length) {
            // restore all options from backup
            state.predicate_autocomplete = state.predicate_autocomplete_all
        } else {
            filteredOptions.forEach(op => predicates.add(op['association']['predicate']) );
            state.predicate_autocomplete = [...predicates]
        }

        // INPUT
        if (state.output_selected.length && !state.input_selected.length) {
            filteredOptions.forEach(op => inputs.add(op['association']['input_type']) );
            state.input_autocomplete = [...inputs]
        } else if (state.input_selected.length && !state.output_selected.length) {
            //OUTPUT
            filteredOptions.forEach(op => outputs.add(op['association']['output_type']) );
            state.output_autocomplete = [...inputs]
        } else {
            filteredOptions.forEach(op => {
            outputs.add(op['association']['output_type'])
            inputs.add(op['association']['input_type']) 
            });
            state.output_autocomplete = [...outputs]
            state.input_autocomplete = [...inputs]
        }

        const t1 = performance.now();
        var seconds = (((t1 - t0) % 60000) / 1000).toFixed(0);
        console.log(`%c (getNewOptions) Calculating input options took ${seconds} seconds.`, 'color:cyan');

        },
        loadMetaKG(state, payload) {
        state.meta_kg = payload['graph'];
        //Initial data Processing
        const t0 = performance.now();
        //all nodes and edges
        let data = [];
        let nodes = new Set();
        let oac_set = new Set();
        let iac_set = new Set();
        let pac_set = new Set();

        state.operationsTotal = state.meta_kg.ops.length;

        // console.log(state.meta_kg.ops)
        console.log("OPs: "+state.operationsTotal, "Limit: "+state.maxEdgesRendered)

        state.meta_kg.ops.forEach((op, i) => {
            
            nodes.add(op['association']['input_type']);
            nodes.add(op['association']['output_type']);

            if (state.operationsTotal < state.maxEdgesRendered) {
            let edgeName = op['association']['api_name'] + ' : ' + op['association']['predicate'];

            let edge = {
                group: 'edges',
                data: {
                id: edgeName + i,
                name: edgeName,
                predicate: op['association']['predicate'],
                output_id: op['association']['output_id'],
                api_name: op['association']['api_name'],
                type: op['association']['api_name'],
                source: op['association']['input_type'],
                target: op['association']['output_type'],
                }
            };

            data.push(edge);
            state.overEdgeLimit = false
            }else{
            state.overEdgeLimit = true
            }

            // Autocomplete
            oac_set.add(op['association']['output_type']);
            iac_set.add(op['association']['input_type']);
            pac_set.add(op['association']['predicate']);

        });

        state.output_autocomplete = [...oac_set];
        state.input_autocomplete = [...iac_set];
        state.predicate_autocomplete = [...pac_set];


        nodes.forEach(node => {
            data.push({ 
            group: 'nodes',          
            data: {
                name: node,
                id: node
            }
            });
        });

        state.cyto_data = data;

        state.loading = false;

        //save backup of all options for getNewOptions
        state.predicate_autocomplete_all = state.predicate_autocomplete;

        // starting results on left panel
        state.results = state.meta_kg.ops;

        const t1 = performance.now();
        var seconds = (((t1 - t0) % 60000) / 1000).toFixed(0);
        console.log(`%c Parsing initial data took ${seconds} seconds.`, 'color:pink');
        },
        saveResults(state, payload) {
        state.results = payload['res']
        const t0 = performance.now();

        let data = []
        let nodes = new Set()

        state.operationsTotal = state.results.length;
        console.log("OPs: "+state.operationsTotal, "Limit: "+state.maxEdgesRendered)

        state.results.forEach((result, i) => {
            nodes.add(result['association']['input_type'])
            nodes.add(result['association']['output_type'])

            if (state.operationsTotal < state.maxEdgesRendered) {
            let edgeName = result['association']['api_name'] + ' : ' + result['association'][
                'predicate'
            ]

            let edge = {
                group: 'edges',
                data: {
                id: edgeName + i,
                name: edgeName,
                predicate: result['association']['predicate'],
                output_id: result['association']['output_id'],
                api_name: result['association']['api_name'],
                source: result['association']['input_type'],
                target: result['association']['output_type'],
                }
            };
            data.push(edge)
            state.overEdgeLimit = false
            }else{
            state.overEdgeLimit = true
            }
            
        });
        
        nodes.forEach(node => {
            data.push({ 
            group: 'nodes',          
            data: {
                name: node,
                id: node
            }
            });
        });

        state.cyto_data = data

        const t1 = performance.now();
        var seconds = (((t1 - t0) % 60000) / 1000).toFixed(0);
        console.log(`(saveResults) Creating new nodes from search took ${seconds} seconds.`);

        },
        pushPill(state, payload) {
        let type = payload["type"]
        let q = payload["q"]

        switch (type) {
            case 'predicate':
            if (!state.predicate_selected.includes(q)) {
                state.predicate_selected.push(q)
            } else {
                this.$swal.fire({
                type: 'error',
                toast: true,
                title: 'Already Selected',
                showConfirmButton: false,
                timer: 1000
                });
            }

            break;
            case 'input_type':
            if (!state.input_selected.includes(q)) {
                state.input_selected.push(q)
            } else {
                this.$swal.fire({
                type: 'error',
                toast: true,
                title: 'Already Selected',
                showConfirmButton: false,
                timer: 1000
                });
            }

            break;
            case 'output_type':
            if (!state.output_selected.includes(q)) {
                state.output_selected.push(q)
            } else {
                this.$swal.fire({
                type: 'error',
                toast: true,
                title: 'Already Selected',
                showConfirmButton: false,
                timer: 1000
                });
            }

            break;
            default:
            console.log('NO option pushPill')
        }
        },
        removePill(state, payload) {
        let type = payload["type"]
        let q = payload["q"]
        let i = ''

        switch (type) {
            case 'predicate':
            i = state.predicate_selected.indexOf(q);
            state.predicate_selected.splice(i, 1);
            break;
            case 'input_type':
            i = state.input_selected.indexOf(q);
            state.input_selected.splice(i, 1);
            break;
            case 'output_type':
            i = state.output_selected.indexOf(q);
            state.output_selected.splice(i, 1);
            break;
            default:
            console.log('NO option removePill')
        }
        },
        
     },
    actions: {
        handleParams({commit}, payload) {
            let params = payload['params']
    
            params = new URLSearchParams(params);
    
            let array = ['input_type', 'predicate', 'output_type']
    
            for (var x = 0; x < array.length; x++) {
                let current_inputtype = array[x]
    
                let type = params.get(current_inputtype);
                if (type) {
                let selections = type.split(',');
    
                for (var i = 0; i < selections.length; i++) {
                    var payload1 = {};
                    payload1["type"] = current_inputtype;
                    payload1["q"] = selections[i];
                    commit('pushPill', payload1);
    
                    var payload2 = {};
                    payload2["name"] = current_inputtype;
                    payload2["q"] = self.selected;
                    commit('saveInput', payload2);
                }
                }
            }
    
    
        },
        recenterGraph() {
            this.cy.fit();
        },
        highlightThis(payload) {
        let name = payload['highlight']
        let found = this.cy.filter(function (element) {
            if (element.isEdge() && element.data('name').includes(name)) {
            return element;
            }
        });
        found.addClass('highlightedAPI');
        },
        unhighlightThis() {
            this.cy.elements().removeClass('highlightedAPI')
        },
        allWithTag(payload) {
        let name = payload['highlight']

        let found = this.cy.filter(function (element) {
            if (element.isEdge() && element.data('tags').includes(name)) {
            return element;
            }
        });
        found.addClass('highlightedTag')

        },
        allWithTagUndo() {
        this.cy.elements().removeClass('highlightedTag')
        },
        highlightRowAndZoom({
        state
        }, payload) {

        let item = payload['item']
        let p = item['association']['predicate']
        let s = item['association']["input_type"]
        let t = item['association']["output_type"]
        let o = item['association']["output_id"]
        let a = item['association']["api_name"]

        if (state.operationsTotal < state.maxEdgesRendered) {
            let found = this.cy.filter(function (element) {
            if (element.isEdge() && element.data('predicate') == p) {
            if (element.source().data('name') == s && element.target().data('name') == t) {
                if (element.data('output_id') == o && element.data('api_name') == a) {
                return element;
                }
            }
            }
        });
        found.select()
        found.connectedNodes().style({
            'opacity': 1
        })
        this.cy.fit(found, 75)
        }
        },
        highlightRow({
        state
        }, payload) {

        let item = payload['item']
        let p = item['association']['predicate']
        let s = item['association']["input_type"]
        let t = item['association']["output_type"]
        let o = item['association']["output_id"]
        let a = item['association']["api_name"]

        if (state.operationsTotal < state.maxEdgesRendered) {
            let found = this.cy.filter(function (element) {
            if (element.isEdge() && element.data('predicate') == p) {
                if (element.source().data('name') == s && element.target().data('name') == t) {
                if (element.data('output_id') == o && element.data('api_name') == a) {
                    return element;
                }
                }
            }
            });
            found.select()
            found[0].tippy.show()
            found.connectedNodes().style({
            'opacity': 1
            })
        }
        },
        unhighlightRow({
        state
        }, payload) {
        // let name = payload['unhighlight']
        // this.cy.elements().unselect()
        let item = payload['item']
        let p = item['association']['predicate']
        let s = item['association']["input_type"]
        let t = item['association']["output_type"]
        let o = item['association']["output_id"]
        let a = item['association']["api_name"]

        if (state.operationsTotal < state.maxEdgesRendered) {
            let found = this.cy.filter(function (element) {
            if (element.isEdge() && element.data('predicate') == p) {
            if (element.source().data('name') == s && element.target().data('name') == t) {
                if (element.data('output_id') == o && element.data('api_name') == a) {
                return element;
                }
            }
            }
        });
        this.cy.filter('node').style({
            'opacity': 1
        })
        found.unselect()
        found[0].tippy.hide()
        this.cy.filter('node').style({
            'opacity': 1
        })
        }
        },
        handle_metaKG_Query_New({
        commit,
        state
        }) {
        // console.log(state)
        let q = {}
        if (state.output_type && state.output_type.length) {
            q['output_type'] = state.output_type
        }
        if (state.predicate && state.predicate.length) {
            q['predicate'] = state.predicate
        }
        if (state.input_type && state.input_type.length) {
            q['input_type'] = state.input_type
        }

        console.log("%c Executing new query...", "color:lightblue")
        console.log(JSON.stringify(q, null, 2))

        let g = state.meta_kg.filter(q);

        if (g) {
            var payload = {};
            payload["res"] = g;
            commit('saveResults', payload);

            var pay = {};
            pay["res"] = g;
            commit('getNewOptions', pay);

            commit('drawGraph');
        }
        },
        download() {

        let options = {
            "bg": "white",
            "full": true,
            "quality": 1,
            "output": 'blob'
        }

        let pic = this.cy.png(options)

        var a = document.createElement("a");
        var file = new Blob([pic], {
            type: 'image/png'
        });
        a.href = URL.createObjectURL(file);
        a.download = 'meta-kg-graph';
        a.click();

        this.$swal.fire({
            type: 'success',
            toast: true,
            title: 'Success',
            showConfirmButton: false,
            timer: 2000
        });

        },
        buildURL({
        state
        }) {

        let base = window.location.origin + window.location.pathname
        let finalURL = window.location.href
        // console.log('finalURL START',finalURL)
        let url = new URL(finalURL);

        let params = new URLSearchParams(url.search.slice(1));

        if (state.predicate_selected.length) {
            //something is selected
            params.set('predicate', state.predicate_selected.toString());
        } else {
            //nothing selected
            if (params.get('predicate')) {
            params.delete('predicate');
            }
        }

        if (state.input_selected.length) {
            //something is selected
            params.set('input_type', state.input_selected.toString());
        } else {
            //nothing selected
            if (params.get('input_type')) {
            params.delete('input_type');
            }
        }

        if (state.output_selected.length) {
            //something is selected
            params.set('output_type', state.output_selected.toString());
        } else {
            //nothing selected
            if (params.get('output_type')) {
            params.delete('output_type');
            }
        }

        finalURL = base + "?" + params

        //HTML5 change url history
        window.history.pushState({
            "html": 'content',
            "pageTitle": 'SmartAPI'
        }, "MetaKG", finalURL);
        },
     },
    getters: {
        getAPIS: (state) => {
            return state.apis
          },
          getName: (state) => {
            return state.name
          },
          getI_AC: (state) => {
            return state.input_autocomplete
          },
          getP_AC: (state) => {
            return state.predicate_autocomplete
          },
          getO_AC: (state) => {
            return state.output_autocomplete
          },
          getI_Selected: (state) => {
            return state.input_selected
          },
          getP_Selected: (state) => {
            return state.predicate_selected
          },
          getO_Selected: (state) => {
            return state.output_selected
          },
          getHtml: (state) => {
            for (var name in state.portals) {
              if (name == state.name) {
                return state.portals[name]
              }
            }
          },
          getResults: (state) => {
            return state.results
          },
          getCytoData: (state) => {
            return state.cyto_data
          },
          getSpread: (state) => {
            return state.spread
          },
          getTagList: (state) => {
            return state.tagList
          },
          getAPITotal: (state) => {
            return state.operationsTotal
          },
          getLoading: (state) => {
            return state.loading
          },
          getOverEdgeLimit: (state) => {
            return state.overEdgeLimit
          },
          getLimit: (state) => {
            return state.maxEdgesRendered
          },
     }
  }