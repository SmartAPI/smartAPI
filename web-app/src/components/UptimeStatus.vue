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
    props: ['uptime_status', 'err_msg'],
    methods:{
        getStatus(){
        let self = this;
        if (self.uptime_status) {
            switch (self.uptime_status) {
            case 'unknown':
                self.status = 'UNKNOWN';
                self.clss = 'orange';
                break;
            case 'pass':
                self.status = 'PASS';
                self.clss = 'green';
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
        this.getStatus();
        let err_msg = '';
        let err = this.err_msg;
        // if (err && err.includes(":")) {
        //     if (err.includes("http")) {
        //         err_msg = `<tr colspan="2" style="word-break: break-word;" class="red-text pink lighten-5 center">`+
        //         `<td colspan="2"><small>"<b>`
        //         +err+`</b>"`+
        //         `<br>Please provide examples for endpoints that require them.</small></td></tr>`;
        //     } else {
        //         err_msg = err ? `<tr colspan="2" style="word-break: break-word;" class="red-text pink lighten-5 center">`+
        //         `<td colspan="2"><small>"<b>`
        //         +err.split(':')[0]+`</b>"`+
        //         `<br>Failed because: <b>(`+err.split(':')[1]+`)</b></small></td></tr>` :``;
        //     }
        // }
        if (err && err.includes("Everything looks good!")) {
            err_msg = ``
        }else if(err && err.length){
            let allErrors = '' 
            if (Array.isArray(err)) {
                err.forEach((e) => {
                    allErrors += `<p class="red-text"><small>${e}</small></p>`
                });
                err_msg += `<details class="orange lighten-5" style="max-height:400px; overflow:scroll;padding: 10px;">
                    <summary>
                    <b class="red-text">(${err.length}) Issues</b>
                    </summary>
                    ${allErrors}
                </details>`
            }
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
                <div class="white" style="padding:0px;overflow:hidden;">
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
                        <tr class="orange lighten-5">
                            <td colspan='2' class='blue-grey-text'>
                                <small>
                                    <b>UNKNOWN</b> and <b>FAIL</b> statuses can be assigned due to one or more endpoints failing or lacking examples.
                                </small>
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