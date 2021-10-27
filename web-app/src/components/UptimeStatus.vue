<template>
    <div class="apiStatus pointer uptime-status" :class="'us'+badgeID">
        <div>
            Uptime
        </div>
        <div class="white-text center-align" :class='clss'>
            {{ status }}
        </div>
    </div>
</template>

<script>
import tippy from 'tippy.js'

export default {
    name: "UptimeStatus",
    data: function(){
        return{
        status:'',
        clss:'',
        badgeID: Math.floor(Math.random()*90000) + 10000
        }
    },
    props: ['api'],
    methods:{
        getStatus(api){
        let self = this;
        if (api?._status?.uptime_status) {
            let stat = api['_status']['uptime_status'];
            switch (stat) {
            case 'unknown':
                self.status = 'UNKNOWN';
                self.clss = 'orange';
                break;
            case 'good':
                self.status = 'PASS';
                self.clss = 'green';
                break;
            case 'bad':
                self.status = 'FAIL';
                self.clss = 'red';
                break;
            case 'fail':
                self.status = 'FAIL';
                self.clss = 'red';
                break;
            case 'incompatible':
                self.status = 'INCOMPATIBLE';
                self.clss = 'blue';
                break;
            default:
            self.status = 'N/A';
            self.clss = 'grey';
            }
        }else{
            self.status = 'N/A';
            self.clss = 'grey';
        }
        },
    },
    mounted: function(){
        this.getStatus(this.api);
        let err_msg = '';
        let err = this.api?._status?.uptime_msg;
        if (err && err.includes(":")) {
            err_msg = err ? `<tr colspan="2" class="red-text pink lighten-5 center">`+
            `<td colspan="2"><br>"<b>`
            +err.split(':')[0]+`</b>"`+
            `<br>Failed because: <b>(`+err.split(':')[1]+`)</b></small></td></tr>` :``;
        }
        /*eslint-disable */
        tippy('.us'+this.badgeID, {
            placement: 'left-end',
            appendTo: document.body,
            theme:'light',
            interactive:true,
            trigger:'click',
            animation: false,
            allowHTML: true,
            onShow:function (instance) {
                instance.setContent(`
                <div class="white" style="padding:0px;">
                    <table>
                        <thead>
                        `+err_msg+`
                        <tr>
                            <td colspan="2" class='grey-text center'>
                            <b>Overall API Endpoint Uptime Status</b>
                            </td>
                        </tr>
                        </thead>
                        <tbody>
                        <tr>
                            <td class='green-text center'>
                            <b>PASS</b>
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
                </div>`)
            }
         });
         /*eslint-enable */
    },
}
</script>