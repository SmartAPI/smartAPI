<template>
  <div class="apiStatus pointer source-status" :class="'ss' + badgeID">
    <div>Source</div>
    <div class="white-text center-align" :class="clss">
      {{ status }}
    </div>
  </div>
</template>

<script>
import tippy from 'tippy.js';

export default {
  name: 'SourceStatus',
  data: function () {
    return {
      status: '',
      clss: '',
      badgeID: Math.floor(Math.random() * 90000) + 10000
    };
  },
  props: ['refresh_status'],
  methods: {
    getStatus() {
      let self = this;
      if (self.refresh_status) {
        switch (self.refresh_status) {
          case 200:
            self.status = 'OK';
            self.clss = 'green';
            break;
          case 299:
            self.status = 'OK';
            self.clss = 'green';
            break;
          case 499:
            self.status = 'INVALID';
            self.clss = 'red';
            break;
          case 599:
            self.status = 'BROKEN';
            self.clss = 'purple';
            break;
          case 404:
            self.status = 'NOT FOUND';
            self.clss = 'orange';
            break;
          default:
            self.status = self.refresh_status;
            self.clss = 'black';
        }
      } else {
        self.status = 'N/A';
        self.clss = 'grey darken-1';
      }
    }
  },
  mounted: function () {
    this.getStatus();

    /*eslint-disable */
    tippy('.ss' + this.badgeID, {
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
      appendTo: document.body,
      theme: 'light',
      interactive: true,
      trigger: 'click',
      animation: false,
      allowHTML: true
    });
    /*eslint-enable */
  }
};
</script>
