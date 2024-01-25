<template>
  <div class="summary_chart">
    <template v-if="summary_type == 'Uptime_Status'">
      <a class="moreInfo" href="javascript:void(0);" :class="'whatIsUptime' + badgeID"
        ><i class="fa fa-info-circle" aria-hidden="true" title=" What does this mean?"></i
      ></a>
    </template>
    <template v-if="summary_type == 'Source_Status'">
      <a class="moreInfo" href="javascript:void(0);" :class="'whatIsSource' + badgeID"
        ><i class="fa fa-info-circle" aria-hidden="true" title=" What does this mean?"></i
      ></a>
    </template>
    <canvas :id="summary_type" width="600" height="600" :class="tipClass"></canvas>
    <div class="p-1">
      <button
        class="smallButton"
        style="color: white !important"
        :class="showDetails ? 'red white-text-imp' : 'grey'"
        v-text="showDetails ? 'Close' : 'Details'"
        @click="
          showDetails = !showDetails;
          makeTable(tableData);
          filter = 'All';
          bgColor = 'grey';
        "
      ></button>
    </div>
    <div class="p-1">
      <h6
        class="white-text p-1"
        :style="{ backgroundColor: bgColor }"
        v-show="filter && showDetails"
        v-text="filter"
      ></h6>
      <div v-show="showDetails" :id="summary_type + 'table'"></div>
    </div>
  </div>
</template>

<script>
import Chart from 'chart.js';
import Tabulator from 'tabulator-tables';
import axios from 'axios';
import tippy from 'tippy.js';

export default {
  name: 'SummaryChart',
  data: function () {
    return {
      tipClass: '',
      showDetails: false,
      tableData: [],
      filter: '',
      bgColor: '',
      analytics: Object,
      badgeID: Math.floor(Math.random() * 90000) + 10000
    };
  },
  props: ['data', 'summary_type', 'colors', 'apiname'],
  methods: {
    handleChartClick(label, color) {
      let filtered = this.tableData.filter((d) => d.label.includes(label));
      this.filter = label;
      this.bgColor = color;
      this.showDetails = true;
      this.makeTable(filtered, true);
    },
    makeTable(data, hideSecondCol) {
      if (this.showDetails) {
        new Tabulator('#' + this.summary_type + 'table', {
          height: 300, // set height of table (in CSS or here), this enables the Virtual DOM and improves render speed dramatically
          data: data,
          layout: 'fitColumns',
          columns: [
            {
              title: 'API',
              field: 'name',
              formatter: function (cell) {
                var value = cell.getValue();
                cell.getElement().style.whiteSpace = 'pre-wrap';
                return (
                  "<b class='blue-text'>" +
                  value +
                  " <i class='material-icons tiny blue-text'>launch</i></b>"
                );
              }
            },
            hideSecondCol
              ? { title: '', visible: false }
              : {
                  title: this.summary_type.replaceAll('_', ' '),
                  field: 'label',
                  formatter: 'textarea'
                }
          ],
          rowClick: function (e, row) {
            var a = document.createElement('a');
            a.href = '/registry?q=' + row.getData().id;
            a.target = '_blank';
            a.click();
          }
        });
      }
    },
    getRandomColor() {
      var letters = '0123456789ABCDEF';
      var color = '#';
      for (var i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
      }
      return color;
    },
    getRandomColors(numberOfColors) {
      let colors = [];
      for (var i = 0; i < numberOfColors; i++) {
        colors.push(this.getRandomColor());
      }
      return colors;
    },
    byTeamsIn(field) {
      let self = this;
      let teams = {};
      //console.log('By Teams in: '+field)

      self.data.forEach((item) => {
        if (
          Object.prototype.hasOwnProperty.call(item['info'], field) &&
          Object.prototype.hasOwnProperty.call(item['info'][field], 'team')
        ) {
          self.tableData.push({
            id: item['_id'],
            name: item['info']['title'],
            label: item['info'][field]['team'].toString()
          });
          if (typeof item['info'][field]['team'] !== 'string') {
            item['info'][field]['team'].forEach((team) => {
              if (team in teams) {
                teams[team]++;
              } else {
                teams[team] = 1;
              }
            });
          } else {
            if (item['info'][field]['team'] in teams) {
              teams[item['info'][field]['team']]++;
            } else {
              teams[item['info'][field]['team']] = 1;
            }
          }
        }
      });

      let teams_sorted = Object.fromEntries(
        Object.entries(teams)
          .sort(([, a], [, b]) => a - b)
          .reverse()
      );

      let data = {
        datasets: [
          {
            data: Object.values(teams_sorted),
            backgroundColor:
              self.colors == 'random'
                ? self.getRandomColors(Object.keys(teams_sorted).length)
                : self.colors
          }
        ],
        labels: Object.keys(teams_sorted)
      };
      self.drawHorBarChart(data);
    },
    byComponentsIn(field) {
      let self = this;
      let components = {};
      //console.log('By Components in: '+field)

      self.data.forEach((item) => {
        if (
          Object.prototype.hasOwnProperty.call(item['info'], field) &&
          Object.prototype.hasOwnProperty.call(item['info'][field], 'component')
        ) {
          self.tableData.push({
            id: item['_id'],
            name: item['info']['title'],
            label: item['info'][field]['component']
          });
          if (typeof item['info'][field]['component'] !== 'string') {
            item['info'][field]['component'].forEach((c) => {
              if (c in components) {
                components[c]++;
              } else {
                components[c] = 1;
              }
            });
          } else {
            if (item['info'][field]['component'] in components) {
              components[item['info'][field]['component']]++;
            } else {
              components[item['info'][field]['component']] = 1;
            }
          }
        }
      });

      let components_sorted = Object.fromEntries(
        Object.entries(components)
          .sort(([, a], [, b]) => a - b)
          .reverse()
      );

      let data = {
        datasets: [
          {
            data: Object.values(components_sorted),
            backgroundColor:
              self.colors == 'random'
                ? self.getRandomColors(Object.keys(components_sorted).length)
                : self.colors
          }
        ],
        labels: Object.keys(components_sorted)
      };
      self.drawBarChart(data, true);
    },
    byStatus(field) {
      let self = this;
      let statuses = {};

      if (field == 'uptime_status') {
        statuses = {
          pass: 0,
          unknown: 0,
          incompatible: 0,
          fail: 0
        };
      }

      self.data.forEach((item) => {
        if (Object.prototype.hasOwnProperty.call(item['_status'], field)) {
          //table data
          if (field == 'refresh_status') {
            self.tableData.push({
              id: item['_id'],
              name: item['info']['title'],
              label:
                item['_status'][field] == '200'
                  ? 'OK'
                  : item['_status'][field] == '299'
                  ? 'OK'
                  : item['_status'][field] == '404'
                  ? 'Not Found'
                  : item['_status'][field] == '499'
                  ? 'Invalid'
                  : 'Broken'
            });
          } else {
            self.tableData.push({
              id: item['_id'],
              name: item['info']['title'],
              label: item['_status'][field]
            });
          }
          //chart data
          if (item['_status'][field] in statuses) {
            statuses[item['_status'][field]]++;
          } else {
            statuses[item['_status'][field]] = 1;
          }
        }
      });

      if (field == 'refresh_status') {
        // assign UI used names
        let with_labels = { OK: 0, 'Not Found': 0, Invalid: 0, Broken: 0 };
        for (const key in statuses) {
          switch (key) {
            case '200':
              with_labels['OK'] += statuses[key];
              break;
            case '299':
              with_labels['OK'] += statuses[key];
              break;
            case '404':
              with_labels['Not Found'] += statuses[key];
              break;
            case '499':
              with_labels['Invalid'] += statuses[key];
              break;
            default:
              with_labels['Broken'] += statuses[key];
              break;
          }
        }
        statuses = with_labels;
      }

      let data = {
        datasets: [
          {
            data: Object.values(statuses),
            backgroundColor:
              self.colors == 'random'
                ? self.getRandomColors(Object.keys(statuses).length)
                : self.colors
          }
        ],
        labels: Object.keys(statuses)
      };

      self.drawPieChart(data);
    },
    hasFieldAndTag(field, tag) {
      let self = this;
      let yesTF = 0;
      let noTF = 0;
      let yesTnoF = 0;
      let noTyesF = 0;

      let yesTF_label = `✅ Tagged "${tag}" ✅ Ext -${field}`;
      let yesTnoF_label = `✅ Tagged "${tag}" ❌ Ext -${field}`;
      let noTF_label = `❌ Tagged "${tag}" ❌ Ext -${field}`;
      let noTyesF_label = `❌ Tagged "${tag}" ✅ Ext -${field}`;

      self.data.forEach((item) => {
        if (
          Object.prototype.hasOwnProperty.call(item, 'tags') &&
          JSON.stringify(item['tags']).includes(tag)
        ) {
          if (Object.prototype.hasOwnProperty.call(item['info'], field)) {
            yesTF++;
            self.tableData.push({
              id: item['_id'],
              name: item['info']['title'],
              label: yesTF_label
            });
          } else {
            yesTnoF++;
            self.tableData.push({
              id: item['_id'],
              name: item['info']['title'],
              label: yesTnoF_label
            });
          }
        } else {
          if (Object.prototype.hasOwnProperty.call(item['info'], field)) {
            noTyesF++;
            self.tableData.push({
              id: item['_id'],
              name: item['info']['title'],
              label: noTyesF_label
            });
          } else {
            noTF++;
            self.tableData.push({
              id: item['_id'],
              name: item['info']['title'],
              label: noTF_label
            });
          }
        }
      });

      let data = {
        datasets: [
          {
            data: [],
            backgroundColor: []
          }
        ],
        labels: []
      };

      data.datasets[0].data.push(yesTF);
      data.labels.push(yesTF_label);
      data.datasets[0].backgroundColor.push('#20c96a');

      data.datasets[0].data.push(yesTnoF);
      data.labels.push(yesTnoF_label);
      data.datasets[0].backgroundColor.push('#ffbf47');

      data.datasets[0].data.push(noTyesF);
      data.labels.push(noTyesF_label);
      data.datasets[0].backgroundColor.push('#925ed6');

      if (self.summary_type !== 'x-trapi_Compliant') {
        noTF
          ? (data.datasets[0].data.push(noTF),
            data.labels.push(noTF_label),
            data.datasets[0].backgroundColor.push('#e65a78'))
          : false;
      }

      self.drawDoughnutChart(data);
    },
    byUserInteractions(apiname) {
      let self = this;
      axios
        .get(
          '	https://gasuperproxy-1470690417190.appspot.com/query?id=ahxzfmdhc3VwZXJwcm94eS0xNDcwNjkwNDE3MTkwchULEghBcGlRdWVyeRiAgIDMgsmRCgw'
        )
        .then((res) => {
          if (res.data.rows) {
            self.analytics = res.data.rows;
            let data = { labels: [], datasets: [] };
            let label = '';
            let dataArray = [];

            for (var i = 0; i < self.analytics.length; i++) {
              if (self.analytics[i][1].toLowerCase() === apiname.toLowerCase()) {
                label = self.analytics[i][0].toUpperCase();
                if (label == 'EXPANDED') {
                  label = 'VIEWS';
                }
                data.labels.push(label);
                let number = self.analytics[i][2];
                self.tableData.push({
                  id: i,
                  name: label,
                  label: number
                });
                dataArray.push(number);
              }
            }
            data.datasets.push({
              label: 'Users',
              data: dataArray,
              backgroundColor: ['#3e95cd', '#8e5ea2', '#3cba9f', '#e8c3b9', '#c45850']
            });
            self.drawBarChart(data, false);
          }
        })
        .catch((err) => {
          self.$toast.error(`Failed to get user interactions`);
          throw err;
        });
    },
    drawDoughnutChart(data) {
      let self = this;
      var ctx = document.getElementById(this.summary_type);

      new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
          title: {
            display: true,
            text:
              self.summary_type.replace('_', ' ') +
              ' (' +
              data.datasets[0].data.reduce((a, b) => a + b, 0) +
              ')',
            fontColor: 'black',
            fontSize: '20'
          },
          legend: {
            position: 'top',
            labels: {
              fontColor: 'grey'
            }
          },
          onClick: function (e, item) {
            if (item.length && Object.prototype.hasOwnProperty.call(item[0], '_view')) {
              self.handleChartClick(item[0]._view.label, item[0]._view.backgroundColor);
            } else {
              self.showDetails = false;
            }
          }
        }
      });
    },
    drawPieChart(data) {
      let self = this;
      var ctx = document.getElementById(this.summary_type);

      new Chart(ctx, {
        type: 'pie',
        data: data,
        options: {
          title: {
            display: true,
            text:
              self.summary_type.replace('_', ' ') +
              ' (' +
              data.datasets[0].data.reduce((a, b) => a + b, 0) +
              ')',
            fontColor: 'black',
            fontSize: '20'
          },
          onClick: function (e, item) {
            if (item.length && Object.prototype.hasOwnProperty.call(item[0], '_view')) {
              self.handleChartClick(item[0]._view.label, item[0]._view.backgroundColor);
            } else {
              self.showDetails = false;
            }
          }
        }
      });
    },
    drawHorBarChart(data) {
      let self = this;
      var ctx = document.getElementById(this.summary_type);

      new Chart(ctx, {
        type: 'horizontalBar',
        data: data,
        options: {
          title: {
            display: true,
            text:
              self.summary_type.replaceAll('_', ' ') +
              ' (' +
              data.datasets[0].data.reduce((a, b) => a + b, 0) +
              ')',
            fontColor: 'black',
            fontSize: '20'
          },
          legend: {
            display: false
          },
          scales: {
            yAxes: [
              {
                ticks: {
                  precision: 0
                }
              }
            ]
          },
          onClick: function (e, item) {
            if (item.length && Object.prototype.hasOwnProperty.call(item[0], '_view')) {
              self.handleChartClick(item[0]._view.label, item[0]._view.backgroundColor);
            } else {
              self.showDetails = false;
            }
          }
        }
      });
    },
    drawBarChart(data, includeTotal) {
      let self = this;
      var ctx = document.getElementById(this.summary_type);

      new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
          title: {
            display: true,
            text: includeTotal
              ? self.summary_type.replaceAll('_', ' ') +
                ' (' +
                data.datasets[0].data.reduce((a, b) => a + b, 0) +
                ')'
              : self.summary_type.replaceAll('_', ' '),
            fontColor: 'black',
            fontSize: '20'
          },
          legend: {
            display: false
          },
          scales: {
            yAxes: [
              {
                ticks: {
                  precision: 0
                }
              }
            ]
          },
          onClick: function (e, item) {
            if (item.length && Object.prototype.hasOwnProperty.call(item[0], '_view')) {
              self.handleChartClick(item[0]._view.label, item[0]._view.backgroundColor);
            } else {
              self.showDetails = false;
            }
          }
        }
      });
    },
    handleSummary(type) {
      //console.log('%c Summary Type: '+type, 'color:white; background-color:black;padding:2px;')
      switch (type) {
        case 'x-translator_Compliant':
          this.hasFieldAndTag('x-translator', 'translator');
          break;
        case 'x-trapi_Compliant':
          this.hasFieldAndTag('x-trapi', 'trapi');
          break;
        case 'By_Teams':
          this.byTeamsIn('x-translator');
          break;
        case 'By_Component':
          this.byComponentsIn('x-translator');
          break;
        case 'Uptime_Status':
          this.byStatus('uptime_status');
          this.tipClass = 'apiStatus';
          break;
        case 'Source_Status':
          this.byStatus('refresh_status');
          this.tipClass = 'urlStatus';
          break;
        case 'User_Interactions':
          this.byUserInteractions(this.apiname);
          break;
        default:
          break;
      }
    }
  },
  mounted: function () {
    this.handleSummary(this.summary_type);

    /*eslint-disable */
    tippy('.whatIsUptime' + this.badgeID, {
      placement: 'left-end',
      appendTo: document.body,
      theme: 'light',
      interactive: true,
      trigger: 'click',
      animation: false,
      allowHTML: true,
      onShow: function (instance) {
        instance.setContent(`
                <div class="white" style="padding:0px;">
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
                </div>`);
      }
    });
    /*eslint-enable */

    /*eslint-disable */
    tippy('.whatIsSource' + this.badgeID, {
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

<style lang="css">
.summary_chart {
  flex-basis: 40%;
  min-width: 300px;
  max-width: 350px;
  padding: 20px;
  position: relative;
}
.moreInfo {
  position: absolute;
  right: 60px;
  top: 30px;
}
</style>
