import cytoscape from 'cytoscape'
import popper from 'cytoscape-popper';
import tippy from 'tippy.js';
import swal from 'vue-sweetalert2'
import ForceGraph3D from '3d-force-graph';
import {CSS2DRenderer, CSS2DObject} from 'three-css2drender'
import axios from 'axios'

cytoscape.use(popper);

export const metakg = {
    state: () => ({ 
        "useAPI": true,
        "meta_kg": null,
        "results": [],
        "output_autocomplete": [],
        "input_autocomplete": [],
        "predicate_autocomplete": [],
        "output_type": [],
        "input_type": [],
        "predicate": [],
        "component": 'KP',
        'cy': null,
        "predicate_selected": [],
        "input_selected": [],
        "output_selected": [],
        "operationsTotal": 0,
        "loading": false,
        "predicate_autocomplete_all": [],
        'overEdgeLimit': false,
        'showAllEdges': true,
        //set to 0 if no max
        'maxEdgesRendered': 1500,
        'edgeData': [],
        'nodeData':[],
        'showSelfReferenced': false,
        'usingCytoscape': false
     }),
    strict: true,
    mutations: {
        saveComponent(state, payload){
            console.log("💚 Component Change: ", payload.value)
            state.component = payload.value;
        },
        setUseAPI(state, payload) {
            state.useAPI = payload.value;
        },
        toggleLoading(state, payload) {
            state.loading = payload['loading'];
        },
        toggleSelfReferenced(state) {
            state.showSelfReferenced = !state.showSelfReferenced
        },
        setMax(state, payload) {
            state.maxEdgesRendered = payload['value']
        },
        setRenderer(state, payload) {
            state.usingCytoscape = payload['value']
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
        saveMetaKG(state, payload) {
            state.meta_kg = payload['metakg']
        },
        drawGraph(state) {
            let data = {
                nodes: state.nodeData.map(d=>d.data),
                links: state.edgeData.map(d=>d.data)
            }
            const elem = document.getElementById('3d-graph');
            // console.log("DATA", data)
            const Graph = ForceGraph3D({
                extraRenderers: [new CSS2DRenderer()]
            })
            Graph(elem);
            Graph.forceEngine('ngraph')
                .cooldownTicks(10)
                .nodeAutoColorBy('user')
                .graphData(data)
                .width(1200)
                .nodeResolution(16)
                .height(900)
                .backgroundColor('white')
                .nodeThreeObject(node => {
                    const nodeEl = document.createElement('div');
                    nodeEl.textContent = node.id;
                    nodeEl.style.color = '#f2f2f2';
                    nodeEl.className = 'node-label';
                    return new CSS2DObject(nodeEl);
                })
                .nodeThreeObjectExtend(true)
                .enableNavigationControls(true)
                // TODO not working or wonky movement
                // .onNodeHover(node => elem.style.cursor = node ? 'pointer' : null)
                // .onNodeClick(node => {
                //     // Aim at node from outside it
                //     console.log('NODE', node)
                //     if(node?.__threeObj?.position?.x){
                //         const distance = 80;
                //         const distRatio = 1 + distance/Math.hypot(node.__threeObj.position.x, node.__threeObj.position.y, node.__threeObj.position.z);
                //         Graph.cameraPosition(
                //             { x: node.__threeObj.position.x * distRatio, y: node.__threeObj.position.y * distRatio, z: node.__threeObj.position.z * distRatio }, // new position
                //             node, // lookAt ({ x, y, z })
                //             2000  // ms transition duration
                //         );
                //     }
                // })
                // .enableNodeDrag(true)
                // .onNodeDragEnd(node => {
                //     if(node?.__threeObj?.position?.x){
                //         node.fx = node?.__threeObj?.position?.x;
                //         node.fy = node?.__threeObj?.position?.y;
                //         node.fz = node?.__threeObj?.position?.z;
                //     }
                // })
                .linkLabel('html')
                .onLinkHover(node => elem.style.cursor = node ? 'pointer' : null)
                .onLinkClick(link => {
                    window.open('/registry?q='+link.smartapi_id, '_blank');
                });

            if(state.showSelfReferenced){
                Graph
                // .linkDirectionalArrowLength(1)
                // .linkDirectionalArrowRelPos(1)
                .linkCurvature(0.25)
            }
            // fit to canvas when engine stops
            Graph.onEngineStop(() => Graph.zoomToFit(500));
        },
        drawGraphCyto(state) {
            const t0 = performance.now();
            state.cy = cytoscape({
                container: document.getElementById('cy'),
                elements: [...state.edgeData, ...state.nodeData],
                hideEdgesOnViewport: true,
                style: [
                    {
                        selector: 'node',
                        style: {
                        'content': 'data(name)',
                        'min-zoomed-font-size': '2em',
                        "text-valign": "center",
                        "text-halign": "center",
                        'color': 'white',
                        'font-size': '4em',
                        'text-outline-width': 4,
                        'text-outline-color': '#9c27b0',
                        'background-color': '#9c27b0',
                        'z-index': 1000,
                        'width': 'data(weight)',
                        'height': 'data(weight)'
                        }
                    },
                    {
                        selector: 'node:selected',
                        style:{
                        'background-color': 'lightblue',
                        }
                    },
                    {
                        selector: 'edge',
                        style:{
                        'curve-style': state.showSelfReferenced ? 'straight' : 'haystack',
                        'line-color': 'grey',
                        'opacity':.1,
                        'target-arrow-shape': 'triangle',
                        'target-arrow-color': '#257FC5',
                        'width': 10,
                        'z-index': 1,
                        }
                    },
                    {
                        selector: 'edge:selected',
                        style:{
                        'z-index': 1000,
                        'color': '#9c27b0',
                        'font-size': '2.5em',
                        'width': 15,
                        'opacity':1,
                        'line-color': '#f24141',
                        'target-arrow-color': '#f24141',
                        'arrow-scale': 1
                        }
                    },
                    {
                        selector: '.highlightedTag',
                        style:{
                        'line-color': '#673782',
                        'target-arrow-color': '#f24141',
                        'width': 10,
                        }
                    },
                    {
                        selector: '.highlightedAPI',
                        style:{
                        'line-color': 'red',
                        'target-arrow-color': '#f24141',
                        'width': 10,
                        }
                    },
                ]
            })

            state.cy.on('mouseover', 'edge', function(evt){
                evt.target.select()
            });

            state.cy.on('mouseout', 'edge', function(evt){
                evt.target.deselect()
            });

            
            function makePopper(ele) {
                let ref = ele.popperRef();
                ele.tippy = tippy(document.createElement('div'), {
                getReferenceClientRect: ref.getBoundingClientRect,
                hideOnClick: false,
                placement:'top-start',
                trigger: 'manual', // mandatory
                arrow: true,
                interactive: true,
                allowHTML: true,
                theme:'light',
                animation: false,
                appendTo: document.body, // or append dummyDomEle to document.body
                onShow: function(instance){
                    instance.setContent('<div class="purple white-text p-1 center-align"><h4 class="m-1">'+ele.id()+'</h4></div>')
                }
                });
            }

            function makePopperEdge(ele) {
                let ref = ele.popperRef();
                ele.tippy = tippy(document.createElement('div'), {
                getReferenceClientRect: ref.getBoundingClientRect,
                hideOnClick: false,
                trigger: 'manual', // mandatory
                placement:'top-start',
                arrow: true,
                animation: false,
                allowHTML: true,
                interactive: true,
                theme:'light',
                appendTo: document.body, // or append dummyDomEle to document.body
                onShow: function(instance){
                    instance.setContent(`<div class="p-1 text-center"><h6 class="center-align"><a target="_blank" href="http://smart-api.info/registry?q=`+ele.data('smartapi_id')+`">`+ele.data('api_name')+`</a></h6><span class="black-text">`+ele.data('source')+
                    `</span> ➡️ <span class="purple-text">`+ele.data('predicate')+
                    `</span> ➡️ <span class="orange-text">`+ele.data('target')+
                    `</span></div>`)
                }
                });
            }

            state.cy.ready(function () {
                state.cy.elements().forEach(function (ele) {           
                if(!ele.isNode()){
                    makePopperEdge(ele);
                }else{
                    makePopper(ele);
                    ele.data('weight', ele.connectedEdges().length ?  (ele.connectedEdges().length+150) : 150) ;
                }
                });
            });

            state.cy.elements().unbind('mouseover');
            state.cy.elements().bind('mouseover', (event) => event.target.tippy.show());

            state.cy.elements().unbind('mouseout');
            state.cy.elements().bind('mouseout', (event) => event.target.tippy.hide());

            state.cy.elements().bind('click', (event) => {
                event.target.select()
                state.cy.fit(event.target, 75)
            });

            state.cy.elements().unbind('drag');
            state.cy.elements().bind('drag', (event) => event.target.tippy.popperInstance.update());

            state.cy.layout({
                name: "concentric",
                avoidOverlap: true,
                avoidOverlapPadding: 200,
                minNodeSpacing: 200,
            }).run();

            state.cy.maxZoom(2)

            const t1 = performance.now();
            var seconds = (((t1 - t0) % 60000) / 1000).toFixed(0);
            console.log(`%c Rendering graph took ${seconds} seconds.`, 'color:yellow');
        },
        saveContext(state, payload) {
        state.name = payload['context']['portal'];
        },
        saveOperations(state, payload) {
        state.operations = payload['ops'];
        },
        getNewOptionsAPI(state, payload) {
            let filteredOptions = payload['res'];
            const t0 = performance.now();
            let predicates = new Set();
            let inputs = new Set();
            let outputs = new Set();
    
            // PREDICATES
            if (!state.output_selected.length && !state.input_selected.length) {
                // restore all options from backup
                state.predicate_autocomplete = state.predicate_autocomplete_all.sort()
            } else {
                filteredOptions.forEach(op => predicates.add(op['association']['predicate']) );
                state.predicate_autocomplete = [...predicates].sort()
            }
    
            // INPUT
            if (state.output_selected.length && !state.input_selected.length) {
                console.log("💚 Calculating Inputs ", state.output_selected)
                filteredOptions.forEach(op => inputs.add(op['association']['subject']) );
                state.input_autocomplete = [...inputs].sort()
            } else if (state.input_selected.length && !state.output_selected.length) {
                console.log("💚 Calculating Outputs ", state.input_selected)
                //OUTPUT
                filteredOptions.forEach(op => outputs.add(op['association']['object']) );
                state.output_autocomplete = [...outputs].sort()
            } else {
                console.log("💚 Calculating I/O options...")
                filteredOptions.forEach(op => {
                outputs.add(op['association']['object'])
                inputs.add(op['association']['subject']) 
                });
                state.output_autocomplete = [...outputs].sort()
                state.input_autocomplete = [...inputs].sort()
            }
    
            const t1 = performance.now();
            var seconds = (((t1 - t0) % 60000) / 1000).toFixed(0);
            console.log(`%c 💚 (getNewOptionsAPI) Calculating input options took ${seconds} seconds.`, 'color:green');
    
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
                state.predicate_autocomplete = state.predicate_autocomplete_all.sort()
            } else {
                filteredOptions.forEach(op => predicates.add(op['association']['predicate']) );
                state.predicate_autocomplete = [...predicates].sort()
            }
    
            // INPUT
            if (state.output_selected.length && !state.input_selected.length) {
                filteredOptions.forEach(op => inputs.add(op['association']['input_type']) );
                state.input_autocomplete = [...inputs].sort()
            } else if (state.input_selected.length && !state.output_selected.length) {
                //OUTPUT
                filteredOptions.forEach(op => outputs.add(op['association']['output_type']) );
                state.output_autocomplete = [...outputs].sort()
            } else {
                filteredOptions.forEach(op => {
                outputs.add(op['association']['output_type'])
                inputs.add(op['association']['input_type']) 
                });
                state.output_autocomplete = [...outputs].sort()
                state.input_autocomplete = [...inputs].sort()
            }
    
            const t1 = performance.now();
            var seconds = (((t1 - t0) % 60000) / 1000).toFixed(0);
            console.log(`%c (getNewOptions) Calculating input options took ${seconds} seconds.`, 'color:cyan');
    
        },
        createGraphData(state, payload) {
            let results = payload['res'];
            //Initial data Processing
            const t0 = performance.now();
            //all nodes and edges
            let nodes = new Set();
            let all_edges = []
            let all_nodes = []
            //AC
            let oac_set = new Set();
            let iac_set = new Set();
            let pac_set = new Set();
            // color nodes to match active query
            var getNodeColor = name => {
                if (state.input_type.includes(name)) return '#3f51b5 ';
                else if (state.output_type.includes(name)) return 'orange';
                //inactive color
                else return '#df4bfc'
            }

            state.operationsTotal = results.length;
    
            console.log("OPs: "+state.operationsTotal, "Limit: "+state.maxEdgesRendered)
    
            results.forEach(op => {
                nodes.add(op['association']['input_type']);
                nodes.add(op['association']['output_type']);
                let html = `<div class="p-1 center-align white rounded z-depth-3"><h6 class="center-align">`+
                    `<a target="_blank" href="http://smart-api.info/registry?q=`+op['association']['smartapi']['id']+`">`+op['association']['api_name']+`</a>`+
                    `</h6><span class="indigo-text">`+op['association']['input_type']+
                    `</span> ➡️ <span class="purple-text">`+op['association']['predicate']+
                    `</span> ➡️ <span class="orange-text">`+op['association']['output_type']+
                    `</span></div>`

                let edge = {
                    ...op,
                    group: 'edges',
                    data: {
                        id: Math.floor(100000 + Math.random() * 900000),
                        name: op['association']['api_name'] + ' : ' + op['association']['predicate'],
                        html: html,
                        predicate: op['association']['predicate'],
                        output_id: op['association']['output_id'],
                        api_name: op['association']['api_name'],
                        type: op['association']['api_name'],
                        source: op['association']['input_type'],
                        target: op['association']['output_type'],
                        smartapi_id: op['association']['smartapi']['id'],
                        color:'#bf4eff'
                    }
                };
                // edge hover tip
                all_edges.push(edge);
                // Autocomplete
                oac_set.add(op['association']['output_type']);
                iac_set.add(op['association']['input_type']);
                pac_set.add(op['association']['predicate']);
            });
            // autocomplete options
            state.output_autocomplete = [...oac_set];
            state.input_autocomplete = [...iac_set];
            state.predicate_autocomplete = [...pac_set];
            //save backup of all options for getNewOptions
            state.predicate_autocomplete_all = state.predicate_autocomplete;
            state.overEdgeLimit = state.maxEdgesRendered && state.operationsTotal > state.maxEdgesRendered ? true : false;

            //create node data
            nodes.forEach(node => {
                let n = { 
                    group: 'nodes',          
                    data: {
                        id: node,
                        weight: 1,
                        color: getNodeColor(node)
                    }
                }
                n.data.name = state.usingCytoscape ? node : '<div class="purple white-text p-1 center-align rounded"><h4 class="m-1">'+node+'</h4></div>';
                all_nodes.push(n)
            });
            // cap edges if max
            all_edges = state.maxEdgesRendered ? all_edges.slice(0, state.maxEdgesRendered) : all_edges;
            // if max only include nodes on chosen edges
            if (state.maxEdgesRendered) {
                let min_nodes = new Set()
                let min_final = []
                all_edges.forEach(edge => {
                    min_nodes.add(edge.data.source)
                    min_nodes.add(edge.data.target)
                })
                let temp = [...min_nodes]
                temp.forEach(item => {
                    let n = {
                        group: 'nodes',          
                        data: {
                            id: item,
                            weight: 1,
                            color: getNodeColor(item)
                        }
                    }
                    n.data.name = state.usingCytoscape ? item : '<div class="purple white-text p-1 center-align rounded"><h4 class="m-1">'+item+'</h4></div>';
                    min_final.push(n)
                })
                all_nodes = min_final
            }
            // final data
            state.edgeData = all_edges
            state.nodeData = all_nodes
            state.loading = false;
            // starting results on left panel
            state.results = all_edges;
            const t1 = performance.now();
            var seconds = (((t1 - t0) % 60000) / 1000).toFixed(0);
            console.log(`%c 🕧 Creating graph data took ${seconds} seconds.`, 'color:hotpink');
        },
        createGraphDataAPI(state, payload) {
            let results = payload['res'];
            //Initial data Processing
            const t0 = performance.now();
            //all nodes and edges
            let nodes = new Set();
            let all_edges = []
            let all_nodes = []
            //AC
            let oac_set = new Set();
            let iac_set = new Set();
            let pac_set = new Set();
            // color nodes to match active query
            var getNodeColor = name => {
                if (state.input_type.includes(name)) return '#3f51b5 ';
                else if (state.output_type.includes(name)) return 'orange';
                //inactive color
                else return '#df4bfc'
            }

            state.operationsTotal = results.length;
    
            console.log("💚  OPs: "+state.operationsTotal, "Limit: "+state.maxEdgesRendered)
    
            results.forEach(op => {
                let input = op['association']['object']
                let output = op['association']['subject'];
                nodes.add(input);
                nodes.add(output);
                let name = op['association']['api']['name'];
                let id = op['association']['api']['smartapi']['id'];
                let html = `<div class="p-1 center-align white rounded z-depth-3"><h6 class="center-align">`+
                    `<a target="_blank" href="http://smart-api.info/registry?q=`+ id +`">`+ name +`</a>`+
                    `</h6><span class="indigo-text">`+input+
                    `</span> ➡️ <span class="purple-text">`+op['association']['predicate']+
                    `</span> ➡️ <span class="orange-text">`+output+
                    `</span></div>`

                let edge = {
                    ...op,
                    group: 'edges',
                    data: {
                        id: Math.floor(100000 + Math.random() * 900000),
                        name: name + ' : ' + op['association']['predicate'],
                        html: html,
                        predicate: op['association']['predicate'],
                        output_id: op['association']['output_id'],
                        api_name: name,
                        type: name,
                        source: input,
                        target: output,
                        smartapi_id: id,
                        color:'#bf4eff'
                    }
                };
                // edge hover tip
                all_edges.push(edge);
                // Autocomplete
                oac_set.add(output);
                iac_set.add(input);
                pac_set.add(op['association']['predicate']);
            });
            // autocomplete options
            state.output_autocomplete = [...oac_set];
            state.input_autocomplete = [...iac_set];
            state.predicate_autocomplete = [...pac_set];
            //save backup of all options for getNewOptions
            state.predicate_autocomplete_all = state.predicate_autocomplete;
            state.overEdgeLimit = state.maxEdgesRendered && state.operationsTotal > state.maxEdgesRendered ? true : false;

            //create node data
            nodes.forEach(node => {
                let n = { 
                    group: 'nodes',          
                    data: {
                        id: node,
                        weight: 1,
                        color: getNodeColor(node)
                    }
                }
                n.data.name = state.usingCytoscape ? node : '<div class="purple white-text p-1 center-align rounded"><h4 class="m-1">'+node+'</h4></div>';
                all_nodes.push(n)
            });
            // cap edges if max
            all_edges = state.maxEdgesRendered ? all_edges.slice(0, state.maxEdgesRendered) : all_edges;
            // if max only include nodes on chosen edges
            if (state.maxEdgesRendered) {
                let min_nodes = new Set()
                let min_final = []
                all_edges.forEach(edge => {
                    min_nodes.add(edge.data.source)
                    min_nodes.add(edge.data.target)
                })
                let temp = [...min_nodes]
                temp.forEach(item => {
                    let n = {
                        group: 'nodes',          
                        data: {
                            id: item,
                            weight: 1,
                            color: getNodeColor(item)
                        }
                    }
                    n.data.name = state.usingCytoscape ? item : '<div class="purple white-text p-1 center-align rounded"><h4 class="m-1">'+item+'</h4></div>';
                    min_final.push(n)
                })
                all_nodes = min_final
            }
            // final data
            state.edgeData = all_edges
            state.nodeData = all_nodes
            state.loading = false;
            // starting results on left panel
            state.results = all_edges;
            const t1 = performance.now();
            var seconds = (((t1 - t0) % 60000) / 1000).toFixed(0);
            console.log(`%c 🕧 Creating graph data took ${seconds} seconds.`, 'color:hotpink');
        },
        pushPill(state, payload) {
        let type = payload["type"]
        let q = payload["q"]

        switch (type) {
            case 'predicate':
            if (!state.predicate_selected.includes(q)) {
                state.predicate_selected.push(q)
            } else {
                swal({
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
                swal({
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
                swal({
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
        draw({commit, state}){
            state.usingCytoscape ? commit('drawGraphCyto') : commit('drawGraph');
        },
        handleParams({commit, dispatch}, payload) {
            // let found = false;
            let params = payload['params']
            params = new URLSearchParams(params);
            let array = ['input_type', 'predicate', 'output_type']
    
            for (var x = 0; x < array.length; x++) {
                let current_input_type = array[x]
    
                let type = params.get(current_input_type);
                if (type) {
                let selections = type.split(',');
    
                for (var i = 0; i < selections.length; i++) {
                    var payload1 = {};
                    payload1["type"] = current_input_type;
                    payload1["q"] = selections[i];
                    commit('pushPill', payload1);
                    
                    var payload2 = {};
                    payload2["name"] = current_input_type;
                    payload2["q"] = selections[i];
                    commit('saveInput', payload2);

                    // found = true
                    console.log('✨ Activating Existing Query ✨', payload1)
                }
                }
            }

            // found ? dispatch('handleQuery'): false;
            dispatch('handleQuery')
        },
        recenterGraph({state}) {
            if (state.usingCytoscape) state.cy.fit();
        },
        highlightThis({state}, payload) {
        let name = payload['highlight']
        let found = state.cy.filter(function (element) {
            if (element.isEdge() && element.data('name').includes(name)) {
            return element;
            }
        });
        found.addClass('highlightedAPI');
        },
        unhighlightThis({state}) {
            state.cy.elements().removeClass('highlightedAPI')
        },
        highlightRowAndZoom({state}, payload) {
            let item = payload['item']
            if (state.operationsTotal < state.maxEdgesRendered && item.data.id) {
                let found = state.cy.edges().filter(function( ele ){
                    return ele.data('id') == item.data.id;
                });
                if(found){
                    found.select()
                    state.cy.fit(found, 75)
                }
            }
        },
        highlightRow({state}, payload) {
            let item = payload['item']
            if (state.operationsTotal < state.maxEdgesRendered && item.data.id) {
                let found = state.cy.edges().filter(function( ele ){
                    return ele.data('id') == item.data.id;
                });
                if(found){
                    found.select()
                    found[0].tippy.show()
                }
            }
        },
        unhighlightRow({state}, payload) {
            let item = payload['item']
            if (state.operationsTotal < state.maxEdgesRendered && item.data.id) {
                let found = state.cy.edges().filter(function( ele ){
                    return ele.data('id') == item.data.id;
                });
                if(found){
                    found.unselect()
                    found[0].tippy.hide()
                }
            }
        },
        handleQuery({commit, state, dispatch}) {
            console.log("💚 HANDLE NEW QUERY")
            let q = {}
            let urlParams = {}
            if (state.output_type && state.output_type.length) {
                q['output_type'] = state.output_type
                urlParams['object'] = state.output_type
            }
            if (state.predicate && state.predicate.length) {
                q['predicate'] = state.predicate
                urlParams['predicate'] = state.predicate
            }
            if (state.input_type && state.input_type.length) {
                q['input_type'] = state.input_type
                urlParams['subject'] = state.input_type
            }
            // Component
            urlParams['component'] = state.component;

            let g = null 
            if (state.useAPI) {
                console.log("%c 💚 Executing new API query...", "color:limegreen")
                console.log("%c " + JSON.stringify( urlParams, null, 2), "color:limegreen")
                commit('toggleLoading', {loading: true})
                axios.get('https://smart-api.info/api/metakg?', {'params': urlParams}).then((res) => {
                    g = res.data.associations.map((data) => {
                        return {'association': data};
                    });
                    commit('toggleLoading', {loading: false})
                    commit('createGraphDataAPI', {res: g});
                    commit('getNewOptionsAPI', {res: g});
                    dispatch('draw');
                }).catch((err) => {
                    commit('toggleLoading', {loading: false})
                    throw err;
                });
            } else {
                console.log("%c Executing new KG query...", "color:lightblue")
                console.log(JSON.stringify(q, null, 2))
                g = state.meta_kg.filter(q);
                if (g) {
                    commit('createGraphData', {res: g});
                    commit('getNewOptions', {res: g});
                    dispatch('draw');
                }
            }
            

            
        },
        download({state}) {

        let options = {
            "bg": "white",
            "full": true,
            "quality": 1,
            "output": 'blob'
        }

        let pic = state.cy.png(options)

        var a = document.createElement("a");
        var file = new Blob([pic], {
            type: 'image/png'
        });
        a.href = URL.createObjectURL(file);
        a.download = 'meta-kg-graph';
        a.click();

        swal({
            type: 'success',
            toast: true,
            title: 'Success',
            showConfirmButton: false,
            timer: 2000
        });

        },
        buildURL({state}) {

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
        results: (state) => {
            return state.results
        },
        getAPITotal: (state) => {
            return state.operationsTotal
        },
        loading: (state) => {
            return state.loading
        },
        overEdgeLimit: (state) => {
            return state.overEdgeLimit
        },
        getLimit: (state) => {
            return state.maxEdgesRendered
        },
        showSelfReferenced: (state) => {
            return state.showSelfReferenced
        },
        getLimitBool: (state) => {
            return state.maxEdgesRendered ? true : false
        },
        usingCytoscape: (state) => {
            return state.usingCytoscape
        },
        useAPI: (state) => {
            return state.useAPI
        }
    }
}