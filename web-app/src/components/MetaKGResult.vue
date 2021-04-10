<template>
    <div 
    class="collection-item resultRow row"
    @mouseenter="highlightRow(item)"
    @mouseleave="unhighlightRow(item)" 
    style="padding: 3px;">
    <div class="col s12 left">
        <small class="d-block">
            <a target="_blank" rel="noreferrer" :href="'/registry?q='+item.association.smartapi.id">
            <b v-text="item.association.api_name"></b>&nbsp;
            <i @mouseenter="highlightRowAndZoom(item)" @mouseleave="recenterGraph()"
                class="fa fa-search-plus pointer blue-grey-text" aria-hidden="true"></i>
            </a>
            <i class="fa fa-info-circle pointer green-text" :class="'resultInfo'+badgeID" aria-hidden="true"
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

<script>
import axios from 'axios'
import tippy from 'tippy.js'

export default {
    name: 'MetaKGResult',
    props:{
        item:{
            type: Object
        }
    },
    data: function () {
        return {
            'hoverInfo': {},
            badgeID: Math.floor(Math.random()*90000) + 10000
        }
    },
    methods:{
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
        recenterGraph() {
        this.$store.dispatch('recenterGraph')
        },
        createTips() {
        var self = this;

        tippy(".resultInfo"+self.badgeID, {
            trigger: 'click',
            placement: 'top-start',
            appendTo: document.body,
            interactive: true,
            allowHTML: true,
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
    mounted: function(){
        this.createTips()
    }
}
</script>

<style>

</style>