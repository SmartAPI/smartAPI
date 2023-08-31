import cytoscape from 'cytoscape'
import popper from 'cytoscape-popper';
import tippy from 'tippy.js';
import swal from 'vue-sweetalert2'
import ForceGraph3D from '3d-force-graph';
import {CSS2DRenderer, CSS2DObject} from 'three-css2drender'
import axios from 'axios'

cytoscape.use(popper);

// During local dev the python server with the API should be running on port 8000
// On prod nginx will redirect /api calls to the right server automatically

export const metakg = {
    state: () => ({ 
        "baseURL": process.env.NODE_ENV == "development" ? "http://localhost:8000/api/metakg/consolidated" : "/api/metakg/consolidated",
        "finalURL": '',
        "meta_kg": null,
        "results": [],
        "object_options": [],
        "subject_options": [],
        "predicate_options": [],
        "object": [],
        "subject": [],
        "predicate": [],
        "node": [],
        'cy': null,
        "predicate_selected": [],
        "edge_selected": [],
        "input_selected": [],
        "output_selected": [],
        "node_selected": [],
        "operationsTotal": 0,
        "loading": false,
        "predicate_autocomplete_all": [],
        'overEdgeLimit': false,
        'showAllEdges': true,
        //set to 0 if no max
        'maxEdgesRendered': 5000,
        'edgeData': [],
        'nodeData':[],
        'showSelfReferenced': true,
        'usingCytoscape': true,
        'size': 20,
        'edgeColors': {},
        'total': 0,
        'apiTotalFromResponse': [],
        'subjectTotalFromResponse': [],
        'objectTotalFromResponse': [],
        'query_term': '',
        'generalMode': false,
        'expand': new Set(),
        'displayedSubjects': new Set(),
        'displayedObjects': new Set(),
        "kp_options": [],
        "ara_options": [],
        'kp': false,
        'ara': false,
        'araSelected': "",
        'kpSelected': "",
     }),
    strict: true,
    mutations: {
        setKPSelected(state, payload){
            state.kpSelected = payload
        },
        setARASelected(state, payload){
            state.araSelected = payload
        },
        setKP(state, payload){
            state.kp = payload
        },
        setARA(state, payload){
            state.ara = payload
        },
        expandThis(state, payload){
            if (!state.expand.has(payload)) {
                state.expand.add(payload)
            }else{
                state.expand.delete(payload)
            }
            console.log([...state.expand])
        },
        setTerm(state, payload){
            state.query_term = payload;
        },
        setMode(state, payload){
            state.generalMode = payload;
        },
        saveSubjects(state, payload){
            state.subject_options = payload;
            console.log(state.subject_options.length + " subjects saved")
        },
        saveObjects(state, payload){
            state.object_options = payload;
            console.log(state.object_options.length + " objects saved")
        },
        savePredicates(state, payload){
            state.predicate_options = payload;
            console.log(state.predicate_options.length + " predicates saved")
        },
        saveKPs(state, payload){
            state.kp_options = payload;
            console.log(state.kp_options.length + " KP names saved")
        },
        saveARAs(state, payload){
            state.ara_options = payload;
            console.log(state.ara_options.length + " ARA names saved")
        },
        saveTotal(state, payload){
            state.total = payload;
        },
        saveAPITotal(state, payload){
            state.apiTotalFromResponse = payload;
        },
        saveObjectTotal(state, payload){
            state.objectTotalFromResponse = payload;
        },
        saveSubjectTotal(state, payload){
            state.subjectTotalFromResponse = payload;
        },
        setSize(state, payload){
            state.size = payload;
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
            if (state.edge_selected.length) {
                state.edge_selected = [];
            }
            if (state.input_selected.length) {
                state.input_selected = [];
            }
            if (state.output_selected.length) {
                state.output_selected = [];
            }
            if (state.node_selected.length) {
                state.node_selected = [];
            }

            state.predicate = [];
            state.subject = [];
            state.object = [];
            state.node = [];
        },
        saveInput(state, payload) {

            let name = payload['name'];

            switch (name) {
                case 'object':
                    state.object = payload["q"]
                    break;
                case 'subject':
                    state.subject = payload["q"]
                    break;
                case 'predicate':
                    state.predicate = payload["q"]
                    break;
                case 'node':
                    state.node = payload["q"]
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
            // const t0 = performance.now();
            function readableName(text){
                const result = text.replace(/([A-Z])/g, " $1");
                return result.charAt(0).toUpperCase() + result.slice(1);
            }

            state.cy = cytoscape({
                container: document.getElementById('cy'),
                elements: [...state.edgeData, ...state.nodeData],
                hideEdgesOnViewport: true,
                style: [
                    {
                        selector: 'node',
                        style: {
                        'content': 'data(name)',
                        'text-wrap': 'wrap',
                        // 'min-zoomed-font-size': '2em',
                        "shape": 'data(shape)',
                        "text-valign": "center",
                        "text-halign": "center",
                        'color': 'white',
                        'font-size': '2em',
                        'text-outline-width': 4,
                        'text-outline-color': state.generalMode ? '#103b56' : 'purple',
                        "background-fill": "radial-gradient",
                        "background-gradient-stop-colors": "data(colors)", // get data from data.color in each node
                        "background-gradient-stop-positions": "25 75 80",
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
                        'curve-style': 'bezier',
                        "label": "data(label)",
                        'font-size': '2em',
                        'text-outline-width': 2,
                        'text-outline-color': 'white',
                        'haystack-radius': 0,
                        'line-color': 'data(color)',
                        'opacity':1,
                        'target-arrow-shape': 'triangle',
                        'target-arrow-color': 'limegreen',
                        'width': "data(label)",
                        'z-index': 1,
                        }
                    },
                    {
                        selector: 'edge:selected',
                        style:{
                        'z-index': 1000,
                        'color': '#9c27b0',
                        // 'font-size': '2.5em',
                        'width': 5,
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
                    instance.setContent('<div class="purple white-text p-small center-align"><h6 class="m-1">'+ readableName(ele.id()) +'</h6></div>')
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

                    let apis_html = '<ul class="browser-default m-0 left-align">';

                    ele.data('apis').forEach(api => {
                        apis_html += `<li><a target="_blank" href="http://smart-api.info/registry?q=`+ api?.['smartapi']?.['id'] +`"><small>`+ api?.name +`</small></a></li>`
                    });

                    apis_html += '</ul>';

                    let html = `
                    <div class="grey lighten-3 center">
                        <small>
                        <b>🟢 ${readableName(ele.data('source'))}</b>
                        <span class="purple-text" style="word-break:break-all;">
                            ${ele.data('predicate')}
                        </span>
                        <b>🟠 ${readableName(ele.data('target'))}</b></small>
                    </div>
                    <details open><summary class="center"><small>` + ele.data('apis').length + ` API(s) available </small></summary>`+ apis_html  +
                    `</details>`;

                    instance.setContent(html)
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
                minNodeSpacing: 90,
            }).run();

            state.cy.maxZoom(2)
            state.cy.minZoom(.5)

            // const t1 = performance.now();
            // var seconds = (((t1 - t0) % 60000) / 1000).toFixed(0);
            // console.log(`%c Rendering graph took ${seconds} seconds.`, 'color: green');
        },
        saveContext(state, payload) {
        state.name = payload['context']['portal'];
        },
        saveOperations(state, payload) {
        state.operations = payload['ops'];
        },
        createGraphDataAPI(state, payload) {
            let results = payload['res'];
            // console.log(JSON.stringify(results[0], null, 2))
            //Initial data Processing
            const t0 = performance.now();
            //all nodes and edges
            let nodes = new Set();
            let all_edges = []
            let all_nodes = []

            state.displayedSubjects.clear();
            state.displayedObjects.clear();
            //AC
            // let oac_set = new Set();
            // let iac_set = new Set();
            // let pac_set = new Set();
            // color nodes to match active query
            var getNodeColor = name => {
                if (state.subject.includes(name)) return '#dce775 #8bc34a';
                else if (state.object.includes(name)) return '#ffca28 #ff9800';
                else if (state.node.includes(name)) return 'hotpink #e91e62';
                //inactive color
                else return state.generalMode ? '#81deea #02838f' : '#df4bfc #4a148c'
            }

            var getNodeShape = name => {
                if (state.subject.includes(name)) {
                    return 'star'
                }
                else if (state.object.includes(name)){
                    return 'star';
                }
                //inactive color
                else return 'ellipse'
            }

            function readableName(text){
                const result = text.replace(/([A-Z])/g, "\n $1");
                return result.charAt(0).toUpperCase() + result.slice(1);
            }

            function getRandomColor() {
                var letters = '0123456789ABCDEF';
                var color = '#';
                for (var i = 0; i < 6; i++) {
                    color += letters[Math.floor(Math.random() * 16)];
                }
                return color;
            }

            state.operationsTotal = results.length;
    
            console.log("💚  OPs: "+state.operationsTotal, "Limit: "+state.maxEdgesRendered)
    
            results.forEach(op => {
                let input = op['subject']
                let output = op['object'];
                nodes.add(input);
                nodes.add(output);
                state.displayedSubjects.add(input);
                state.displayedObjects.add(output);

                // let apis_html = ''
                // op['api'].forEach(api => {
                //     apis_html += `<a target="_blank" href="http://smart-api.info/registry?q=`+ api?.['smartapi']?.['id'] +`">`+ api?.name +`</a>`
                // });

                let name = op._id;
                // let id = op['api'][0]['smartapi']['id'];
                // let html = `<div class="p-1 center-align white rounded z-depth-3"><details>` +
                //     `<summary>` + op.api.length + `</summary>`+ apis_html +
                //     `</details><span class="light-green-text">`+input+
                //     `</span> ➡️ <span class="purple-text">`+op['predicate']+
                //     `</span> ➡️ <span class="orange-text">`+output+
                //     `</span></div>`

                let edge = {
                    ...op,
                    group: 'edges',
                    data: {
                        id: Math.floor(100000 + Math.random() * 900000),
                        // name: name + ' : ' + op['predicate'],
                        name: name,
                        // html: html,
                        predicate: op['predicate'],
                        // output_id: op['output_id'],
                        // api_name: name,
                        // type: name,
                        source: input,
                        target: output,
                        // smartapi_id: id,
                        // component: op['api'][0]['x-translator']['component'],
                        label: op['api'].length,
                        apis: op['api']
                    }
                };
                // edge hover tip
                all_edges.push(edge);
                // Edge Color
                let IO = input + output;
                if (!state.edgeColors[IO]) {
                    state.edgeColors[input + output] = getRandomColor();
                    edge.data.color = state.edgeColors[IO]
                }else{
                    edge.data.color = state.edgeColors[IO]
                }
                // Autocomplete
                // oac_set.add(output);
                // iac_set.add(input);
                // pac_set.add(op['predicate']);
            });
            // autocomplete options
            // state.object_options = [...oac_set];
            // state.subject_options = [...iac_set];
            // state.predicate_options = [...pac_set];
            //save backup of all options for getNewOptions
            state.predicate_autocomplete_all = state.predicate_options;
            state.overEdgeLimit = state.maxEdgesRendered && state.operationsTotal > state.maxEdgesRendered ? true : false;

            //create node data
            nodes.forEach(node => {
                let n = { 
                    group: 'nodes',          
                    data: {
                        id: node,
                        weight: 1,
                        colors: getNodeColor(node)
                    }
                }
                n.data.shape = getNodeShape(node)
                n.data.name = state.usingCytoscape ? readableName(node) : '<div class="purple white-text p-1 center-align rounded"><h4 class="m-1">'+ readableName(node) +'</h4></div>';
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
                            colors: getNodeColor(item)
                        }
                    }
                    n.data.shape = getNodeShape(item)
                    n.data.name = state.usingCytoscape ? readableName(item) : '<div class="purple white-text p-1 center-align rounded"><h4 class="m-1">'+ readableName(item) +'</h4></div>';
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
                icon: 'error',
                toast: true,
                title: 'Already Selected',
                showConfirmButton: false,
                timer: 1000
                });
            }
            break;

            case 'edge':
            if (!state.edge_selected.includes(q)) {
                state.edge_selected.push(q)
            } else {
                swal({
                icon: 'error',
                toast: true,
                title: 'Already Selected',
                showConfirmButton: false,
                timer: 1000
                });
            }

            break;
            case 'subject':
            if (!state.input_selected.includes(q)) {
                state.input_selected.push(q)
            } else {
                swal({
                icon: 'error',
                toast: true,
                title: 'Already Selected',
                showConfirmButton: false,
                timer: 1000
                });
            }

            break;
            case 'object':
            if (!state.output_selected.includes(q)) {
                state.output_selected.push(q)
            } else {
                swal({
                icon: 'error',
                toast: true,
                title: 'Already Selected',
                showConfirmButton: false,
                timer: 1000
                });
            }

            break;

            case 'node':
            if (!state.node_selected.includes(q)) {
                state.node_selected.push(q)
            } else {
                swal({
                icon: 'error',
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
            case 'edge':
            i = state.edge_selected.indexOf(q);
            state.edge_selected.splice(i, 1);
            break;
            case 'subject':
            i = state.input_selected.indexOf(q);
            state.input_selected.splice(i, 1);
            break;
            case 'object':
            i = state.output_selected.indexOf(q);
            state.output_selected.splice(i, 1);
            break;
            case 'node':
            i = state.node_selected.indexOf(q);
            state.node_selected.splice(i, 1);
            break;
            default:
            console.log('NO option removePill')
        }
        },
        buildAPIURL(state, payload){
            let base = state.baseURL.includes('http') ? 
            state.baseURL : window.location.origin + state.baseURL;
            let url = new URL(base);
            for (const key in payload) {
                url.searchParams.append(key, payload[key]);
            }
            state.finalURL = url.href;
        }
     },
    actions: {
        draw({commit, state}){
            state.usingCytoscape ? commit('drawGraphCyto') : commit('drawGraph');
        },
        handleParams({commit, dispatch}, payload) {
            // let found = false;
            let params = payload['params']
            params = new URLSearchParams(params);
            let possibleTypes = ['subject', 'predicate', 'object', 'node', 'edge']
    
            for (var x = 0; x < possibleTypes.length; x++) {
                let currentType = possibleTypes[x]
    
                let type = params.get(currentType);
                if (type) {
                    let selections = type.split(',');
                    if (currentType == 'node' || currentType == 'edge') {
                        commit('setMode', true);
                    }
        
                    for (var i = 0; i < selections.length; i++) {
                        var payload1 = {};
                        payload1["type"] = currentType;
                        payload1["q"] = selections[i];
                        commit('pushPill', payload1);
                        
                        var payload2 = {};
                        payload2["name"] = currentType;
                        payload2["q"] = selections[i];
                        commit('saveInput', payload2);

                        // found = true
                        console.log('✨ Activating Existing Query ✨', JSON.stringify(payload1, null, 2))
                    }
                }
            }

            if (params.get('size')) {
                commit('setSize', params.get('size'))
            }

            if (params.get('api.x-translator.component')) {
                if (params.get('api.x-translator.component').toLowerCase() == 'kp') {
                    commit('setKP', true);
                    if (params.get('api.name')) {
                        commit('setKPSelected', params.get('api.name'));
                    }
                }
                else if (params.get('api.x-translator.component').toLowerCase() == 'ara') {
                    commit('setARA', true);
                    if (params.get('api.name')) {
                        commit('setARASelected', params.get('api.name'));
                    }
                }
            }

            if (params.get('api.name')) {
                if (params.get('api.x-translator.component').toLowerCase() == 'kp') {
                    commit('setKPSelected', params.get('api.name'));
                }
                else if (params.get('api.x-translator.component').toLowerCase() == 'ara') {
                    commit('setARASelected', params.get('api.name'));
                }else{
                    //default
                    commit('setKPSelected', params.get('api.name'));
                }
            }

            if (params.get('expand')) {
                params.get('expand').split('.').forEach((value) => {
                    commit('expandThis', value)
                })
            }

            if (params.get('q')) {
                commit('setTerm', params.get('q'))
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
            console.log("%c New Query", "background: blue; padding: 5px; color: yellow;")
            // let q = {}
            let urlParams = {}
            if (state.object && state.object.length) {
                urlParams['object'] = state.object + ''
            }
            if (state.predicate && state.predicate.length) {
                urlParams['predicate'] = state.predicate  + ''
            }
            if (state.subject && state.subject.length) {
                urlParams['subject'] = state.subject  + ''
            }
            if (state.node && state.node.length) {
                urlParams['node'] = state.node  + ''
            }
            if (state.edge && state.edge.length) {
                urlParams['edge'] = state.edge  + ''
            }
            urlParams['size'] = state.size;

            if (state.expand && state.expand.size) {
                urlParams['expand'] = [...state.expand] + '';
            }

            if (state.kp || state.ara || state.query_term 
                || state.kpSelected || state.araSelected) {
                let q_terms = [];
                if (state.kp) {
                    q_terms.push('api.x-translator.component:KP')
                }
                if (state.kpSelected) {
                    q_terms.push('api.name:' + `"${state.kpSelected}"`)
                }
                if (state.araSelected) {
                    q_terms.push('api.name:' + `"${state.araSelected}"`)
                }
                if (state.ara) {
                    q_terms.push('api.x-translator.component:ARA')
                }
                if (state.query_term) {
                    q_terms.push(`"${state.query_term}"`)
                }
                urlParams['q'] = `(${q_terms.join(' AND ')})`
            }

            urlParams['facet_size'] = 300;
            urlParams['aggs'] = 'api.name.raw,object.raw,subject.raw';
            let g = null 
            console.log("%c " + JSON.stringify( urlParams, null, 2), "color:green; background:lightyellow; padding:5px;")
            // commit('toggleLoading', {loading: true})
            axios.get(state.baseURL, {'params': urlParams}).then((res) => {
                commit('buildAPIURL', urlParams)
                g = res.data?.hits || []
                commit('createGraphDataAPI', {res: g});
                commit('saveTotal', res.data.total);
                commit('saveAPITotal', res.data?.facets?.['api.name.raw']?.terms);
                commit('saveObjectTotal', res.data?.facets?.['object.raw']?.terms);
                commit('saveSubjectTotal', res.data?.facets?.['subject.raw']?.terms);
                dispatch('draw');
            }).catch((err) => {
                throw err;
            });
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

        if (state.kp) {
            params.set('api.x-translator.component', "KP");
        }

        if (state.ara) {
            params.set('api.x-translator.component', "ARA");
        }

        if (state.kpSelected) {
            params.set('api.name', state.kpSelected);
        }

        if (state.araSelected) {
            params.set('api.name', state.araSelected);
        }
        // reset KP/ARA filters  if not active
        if (!state.kp && !state.ara){
            params.delete('api.x-translator.component');
        }

        if( !state.kpSelected && !state.araSelected){
            params.delete('api.name');
        }

        if (state.predicate_selected.length) {
            //something is selected
            params.set('predicate', state.predicate_selected.toString());
        } else {
            //nothing selected
            if (params.get('predicate')) {
            params.delete('predicate');
            }
        }

        if (state.edge_selected.length) {
            //something is selected
            params.set('edge', state.edge_selected.toString());
        } else {
            //nothing selected
            if (params.get('edge')) {
            params.delete('edge');
            }
        }

        if (state.input_selected.length) {
            //something is selected
            params.set('subject', state.input_selected.toString());
        } else {
            //nothing selected
            if (params.get('subject')) {
            params.delete('subject');
            }
        }

        if (state.output_selected.length) {
            //something is selected
            params.set('object', state.output_selected.toString());
        } else {
            //nothing selected
            if (params.get('object')) {
            params.delete('object');
            }
        }

        if (state.node_selected.length) {
            //something is selected
            params.set('node', state.node_selected.toString());
        } else {
            //nothing selected
            if (params.get('node')) {
            params.delete('node');
            }
        }

        params.set('size', state.size);
        
        if (state.expand && state.expand.size) {
            params.set('expand', [...state.expand].toString());
        }else{
            params.delete('expand')
        }

        if (state.query_term) {
            params.set('q', state.query_term);
        }else{
            params.delete('q')
        }

        finalURL = base + "?" + params

        //HTML5 change url history
        window.history.pushState({
            "html": 'content',
            "pageTitle": 'SmartAPI'
        }, "MetaKG", finalURL);
        },
        getOptions({dispatch}) {
            dispatch('getSubjects');
            dispatch('getObjects');
            dispatch('getPredicates');
            dispatch('getComponentNames');
        },
        getSubjects({state, commit}){
            if (!state.subject_options.length) {
                axios.get(state.baseURL + '?aggs=subject.raw&facet_size=200').then(res=>{
                    let data = res.data?.facets?.['subject.raw']?.terms.map(item => item.term).sort();
                    commit('saveSubjects', data);
                }).catch(err=>{
                    console.log('Failed to get subjects', err);
                });
            }
        },
        getObjects({state, commit}){
            if (!state.object_options.length) {
                axios.get(state.baseURL + '?aggs=object.raw&facet_size=200').then(res=>{
                    let data = res.data?.facets?.['object.raw']?.terms.map(item => item.term).sort();
                    commit('saveObjects', data);
                }).catch(err=>{
                    console.log('Failed to get objects', err);
                });
            }
            
        },
        getPredicates({state, commit}){
            if (!state.predicate_options.length) {
                axios.get(state.baseURL + '?aggs=predicate&facet_size=500').then(res=>{
                    let data = res.data?.facets?.predicate?.terms.map(item => item.term).sort();
                    commit('savePredicates', data);
                }).catch(err=>{
                    console.log('Failed to get predicates', err);
                });
            }
        },
        getComponentNames({state, commit}){
            if (!state.kp_options.length) {
                axios.get(state.baseURL + '?size=0&q=(api.x-translator.component:KP)&facet_size=300&aggs=api.name.raw').then(res=>{
                    let data = res.data?.facets?.['api.name.raw']?.terms.map(item => item.term).sort();
                    commit('saveKPs', data);
                }).catch(err=>{
                    console.log('Failed to get KP names', err);
                });
            }

            if (!state.ara_options.length) {
                axios.get(state.baseURL + '?size=0&q=(api.x-translator.component:ARA)&facet_size=300&aggs=api.name.raw').then(res=>{
                    let data = res.data?.facets?.['api.name.raw']?.terms.map(item => item.term).sort();
                    commit('saveARAs', data);
                }).catch(err=>{
                    console.log('Failed to get ARA names', err);
                });
            }
        },
     },
    getters: {
        getSubjectOptions: (state) => {
            return state.subject_options
        },
        getPredicateOptions: (state) => {
            return state.predicate_options
        },
        getObjectOptions: (state) => {
            return state.object_options
        },
        getSubjectSelected: (state) => {
            return state.input_selected
        },
        getPredicateSelected: (state) => {
            return state.predicate_selected
        },
        getEdgeSelected: (state) => {
            return state.edge_selected
        },
        getObjectSelected: (state) => {
            return state.output_selected
        },
        getNode_Selected: (state) => {
            return state.node_selected
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
        size: (state) => {
            return state.size
        },
        finalURL: (state) => {
            return state.finalURL
        },
        expand: (state) => {
            return [...state.expand]
        },
        total: (state) => {
            return state.total
        },
        kp: (state) => {
            return state.kp
        },
        KPNames: (state) => {
            return state.kp_options
        },
        ARANames: (state) => {
            return state.ara_options
        },
        kpSelected: (state) => {
            return state.kpSelected
        },
        araSelected: (state) => {
            return state.araSelected
        },
        ara: (state) => {
            return state.ara
        },
        apiTotalFromResponse: (state) => {
            return state.apiTotalFromResponse
        },
        objectTotalFromResponse: (state) => {
            return state.objectTotalFromResponse
        },
        subjectTotalFromResponse: (state) => {
            return state.subjectTotalFromResponse
        },
        query_term: (state) => {
            return state.query_term
        },
        generalMode: (state) => {
            return state.generalMode
        },
        displayedSubjects: (state) => {
            return [...state.displayedSubjects]
        },
        displayedObjects: (state) => {
            return [...state.displayedObjects]
        },
    }
}