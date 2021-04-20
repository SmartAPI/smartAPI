import cytoscape from 'cytoscape'
import popper from 'cytoscape-popper';
import tippy from 'tippy.js';
import swal from 'vue-sweetalert2'

cytoscape.use(popper);

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
        'maxEdgesRendered': 1500,
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
        saveMetaKG(state, payload) {
            state.meta_kg = payload['metakg']
        },
        drawGraph(state) {
            const t0 = performance.now();

            state.cy.layout({
                name: "concentric",
                avoidOverlap: true,
                avoidOverlapPadding: 200,
                minNodeSpacing: 200,
            }).run();

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
                    instance.setContent('<div class="blue-text p-1 text-center">'+ele.id()+'</div>')
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
                    instance.setContent(`<div class="p-1 text-center"><h6 class="center">`+ele.data('api_name')+`</h6><b class="black-text">`+ele.data('source')+
                    `</b> <b class="purple-text">`+ele.data('predicate')+
                    `</b> <b class="orange-text">`+ele.data('target')+
                    `</b></div>`)
                }
                });
            }

            state.cy.ready(function () {
                state.cy.elements().forEach(function (ele) {           
                if(!ele.isNode()){
                    makePopperEdge(ele);
                }else{
                    makePopper(ele);
                    // console.log('CON', ele.connectedEdges().length)
                    ele.data('weight',  (ele.connectedEdges().length * 2) );
                }
                });
            });

            state.cy.elements().unbind('mouseover');
            state.cy.elements().bind('mouseover', (event) => event.target.tippy.show());

            state.cy.elements().unbind('mouseout');
            state.cy.elements().bind('mouseout', (event) => event.target.tippy.hide());

            state.cy.elements().unbind('drag');
            state.cy.elements().bind('drag', (event) => event.target.tippy.popperInstance.update());

            state.cy.maxZoom(2)

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
        getNewOptions(state) {
            const t0 = performance.now();

            state.output_autocomplete = []
            state.input_autocomplete = []
            state.predicate_autocomplete = []
            
            state.cy.elements().forEach(ele => {    
                !ele.isNode() ? state.predicate_autocomplete.push(ele.data('predicate')) : (state.output_autocomplete.push(ele.data('name')), state.input_autocomplete.push(ele.data('name'))) ;
            });
            const t1 = performance.now();
            var seconds = (((t1 - t0) % 60000) / 1000).toFixed(0);
            console.log(`%c Calculating input options took ${seconds} seconds.`, 'color:cyan');

        },
        loadMetaKG(state, payload) {
            let results = payload['res'];
            //Initial data Processing
            const t0 = performance.now();
            //clear data
            state.cy.elements().remove();
            //all nodes and edges
            let nodes = new Set();
            
            let all_edges = []

            state.operationsTotal = results.length;
    
            console.log("OPs: "+state.operationsTotal, "Limit: "+state.maxEdgesRendered)
    
            results.forEach((op, i) => {

                nodes.add(op['association']['input_type']);
                nodes.add(op['association']['output_type']);
    
                if (i < state.maxEdgesRendered) {
                    // console.log('OP', JSON.stringify(op, null, 2))
                    let edgeName = op['association']['api_name'] + ' : ' + op['association']['predicate'];
        
                    let edge = {
                        ...op,
                        group: 'edges',
                        data: {
                            id: Math.floor(100000 + Math.random() * 900000),
                            name: edgeName,
                            predicate: op['association']['predicate'],
                            output_id: op['association']['output_id'],
                            api_name: op['association']['api_name'],
                            type: op['association']['api_name'],
                            source: op['association']['input_type'],
                            target: op['association']['output_type'],
                        }
                    };
        
                    all_edges.push(edge);
                    state.overEdgeLimit = false
                }else{
                    state.overEdgeLimit = true
                }
    
            });
    
            nodes.forEach(node => {
                state.cy.add({ 
                    group: 'nodes',          
                    data: {
                        name: node,
                        id: node,
                        weight: 1
                    }
                    })
            });

            all_edges.forEach(edge => {
                state.cy.add(edge)
            })
            state.loading = false;
            // starting results on left panel
            state.results = all_edges;
    
            const t1 = performance.now();
            var seconds = (((t1 - t0) % 60000) / 1000).toFixed(0);
            console.log(`%c 🕧 Parsing initial data took ${seconds} seconds.`, 'color:hotpink');
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
        createCy(state){
            state.cy = cytoscape({
                container: document.getElementById('cy'),
                elements: [],
                hideEdgesOnViewport: true,
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
                        'z-index': 1000,
                        // 'width': 'data(weight)',
                        // 'height': 'data(weight)'
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
                        'width': 4,
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
            })
        }
        
     },
    actions: {
        handleParams({commit}, payload) {
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
                    payload2["q"] = self.selected;
                    commit('saveInput', payload2);
                }
                }
            }
        },
        recenterGraph({state}) {
            state.cy.fit();
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
        allWithTag({state}, payload) {
        let name = payload['highlight']

        let found = state.cy.filter(function (element) {
            if (element.isEdge() && element.data('tags').includes(name)) {
            return element;
            }
        });
        found.addClass('highlightedTag')

        },
        allWithTagUndo({state}) {
        state.cy.elements().removeClass('highlightedTag')
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
        handle_metaKG_Query_New({commit, state}) {
            console.log("HANDLE NEW QUERY")
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
                commit('loadMetaKG', {res: g});
                commit('getNewOptions', {res: g});
                commit('drawGraph');
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