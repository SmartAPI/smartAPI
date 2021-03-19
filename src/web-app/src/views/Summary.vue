<template>
  <main id="summary" class="meta_grad summaryContainer" v-cloak>
    <div id="summary2" class="container grey lighten-2 padding20 center-align">
        <div class="chartContainer">
            <div>
                <Image img_name="TranslatorLogo.jpg" aria-label="NCATS" img_height="77px"></Image>
                <p>
                    <router-link to="/portal/translator">Back to Portal</router-link>
                </p>
                <h1>Portal Summary</h1>
                <p>
                    <a href="/registry/translator" v-text="'('+totalAPIs+') Translator APIs'"></a>
                </p>
                
            </div>
        </div>
        <template v-if="summaries && summaries.length">
            <div class="chartContainer">
                <template v-for="summary in summaries" :key="summary.name">
                    <SummaryChart :data="data" :summary_type="summary.name" :colors="summary.colors"></SummaryChart>
                </template>
            </div>
        </template>
    </div>
</main>
</template>

<script>
import SummaryChart from '../components/SummaryChart.vue';
import tippy from 'tippy.js'
import axios from 'axios'

import "tabulator-tables/dist/css/tabulator.css"

export default {
    name: 'Summary',
    components:{
        SummaryChart
    },
    data: function(){
        return {
            summaries: Array,
            totalAPIs: 0
        }
      },
      methods: {
        getSummaries(url){
            let self = this;
            axios.get(url).then(res=>{
                // console.log('ALL RES', res.data)
                self.data = res.data.hits
                self.totalAPIs = res.data.total
                self.summaries = [
                    {'name': 'x-translator_Compliant', 'colors': ["#5ed668", "#ffbf47","#925ed6","#e65a78"]},
                    {'name': 'x-trapi_Compliant', 'colors': ["#5ed668", "#ffbf47","#925ed6","#e65a78"]},
                    {'name': 'By_Teams', 'colors': 'random'},
                    {'name': 'By_Component', 'colors': 'random'},
                    {'name': 'Uptime_Status', 'colors': ["#5ed668","#ffc107","#0277bd","#ff5722"]},
                    {'name': 'Source_Status', 'colors': ["#5ed668","#ffc107","#e65a78","#9c27b0"]},
                ]
            }).catch(err=>{
                throw err;
            });
        },
        initTips(){
                /*eslint-disable */
                tippy( '.urlStatus', {
                    appendTo: document.body,
                    content: `<div class="white" style="padding:0px;">
                                <table>
                                    <thead>
                                    <tr>
                                        <td colspan="2" class='grey-text center'>
                                        <b>API Metadata Source URL Status</b>
                                        </td>
                                    </tr>
                                    </thead>
                                    <tbody>
                                    <tr>
                                        <td class='green-text center'>
                                        <b>OK</b>
                                        </td>
                                        <td class="black-text">
                                        <small>Source URL is working and returns valid metadata.</small>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td class='orange-text center'>
                                        <b>NOT FOUND</b>
                                        </td>
                                        <td class="black-text">
                                        <small>Source URL returns not found.</small>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td class='red-text center'>
                                        <b>INVALID</b>
                                        </td>
                                        <td class="black-text">
                                        <small>Source URL works but contains invalid metadata.</small>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td class='purple-text center'>
                                        <b>BROKEN</b>
                                        </td>
                                        <td class="black-text">
                                        <small>Source URL is broken.</small>
                                        </td>
                                    </tr>
                                    <tr class="cyan lighten-5">
                                        <td colspan='2' class='blue-grey-text'>
                                        <p>
                                            <b>Note: </b> API metadata cannot be synchronized with its source URL if the status is not <b class='green-text'>OK</b>. 
                                        </p>
                                        <p>
                                            <b>Need help?</b> Click on the <b class='indigo-text'>Validate Only</b> button to see issues then the <b class='green-text'>Refresh</b> button once all issues have been resolved.
                                        </p>
                                        </td>
                                    </tr>
                                    </tbody>
                                </table>
                                </div>`,
                        placement: 'left-end',
                        theme:'light',
                        trigger:'click',
                        interactive:true,
                    });

                tippy( '.apiStatus', {
                    appendTo: document.body,
                    content: `<div class="white" style="padding:0px;">
                                <table>
                                <thead>
                                    <tr>
                                    <td colspan="2" class='grey-text center'>
                                        <b>Overall API Endpoint Uptime Status</b>
                                    </td>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                    <td class='green-text center'>
                                        <b>PASS/GOOD</b>
                                    </td>
                                    <td class="black-text">
                                        <small>Your OpenAPI V3 API endpoints provide examples and all return code 200.</small>
                                    </td>
                                    </tr>
                                    <tr>
                                    <td class='red-text center'>
                                        <b>FAIL</b>
                                    </td>
                                    <td class="black-text">
                                        <small>Your OpenAPI V3 API endpoints provide examples but return code other than 200.</small>
                                    </td>
                                    </tr>
                                    <tr> 
                                    <td class='orange-text center'>
                                        <b>UNKNOWN</b>
                                    </td>
                                    <td class="black-text">
                                        <small>None of your OpenAPI V3 API endpoints provide examples and cannot be tested. <a href='/faq#api-monitor' target="_blank">Learn more about how to to enable API status check </a>.</small>
                                    </td>
                                    </tr>
                                    <tr>
                                    <td class='blue-text center'>
                                        <b>INCOMPATIBLE</b>
                                    </td>
                                    <td class="black-text">
                                        <small>Your API's specification does not match OpenAPI V3 specification and will not be tested. Use our guide to learn how to upgrade your metadata to OpenAPI V3 <a href="/guide" target="_blank">here</a>.</small>
                                    </td>
                                    </tr>
                                </tbody>
                                </table>
                            </div>`,
                    placement: 'left-end',
                    theme:'light',
                    trigger:'click',
                    interactive:true,
                });
                /*eslint-enable */
            },
        getPortalData(portal){
            let self = this;
            let url = ''
            switch (portal.toLowerCase()) {
                case 'translator':
                    url = "https://smart-api.info/api/query/?q=__all__&fields=info,tags,_status&size=1000&tags=%22translator%22"
                    self.getSummaries(url)
                    break;
                default:
                    alert(`Portal ${this.$route.params.name} does not exist`)
                    url = ''
                    break;
            }
        }
      },
      mounted: function(){
          this.getPortalData(this.$route.params.name);
          this.initTips();
      }
}
</script>

<style lang="css" scoped>
    .chartContainer{
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        align-items: stretch;
    }
    .summaryContainer{
        width: 100%;
        padding: 2em .5em;
    }
    .white-text-imp{
        color: white !important;
    }
</style>