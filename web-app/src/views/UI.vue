<template>
  <main id="ui-app" class="indexBackground uiBack" style="width: 100%">
    <template v-if="data.api && data.api.info">
      <MetaHead
        :title="'SmartAPI | ' + data.api?.info?.title"
        :description="data.api?.info?.description"
      ></MetaHead>
    </template>
    <teleport to="#uiView" v-if="data.ready">
      <div
        v-if="data.api && data.api._id"
        class="d-flex justify-content-around align-items-center p-1"
      >
        <div class="p-1" style="margin-right: 10px">
          <router-link :to="'/registry?q=' + $route.params.smartapi_id">
            View on SmartAPI Registry
          </router-link>
        </div>
        <div class="d-flex justify-content-around align-items-center p-1">
          <SourceStatus
            style="margin-right: 25px"
            :refresh_status="data?.api?._status?.refresh_status"
          ></SourceStatus>
          <UptimeStatus
            :uptime_status="data?.api?._status?.uptime_status"
            :err_msg="data?.api?._status?.uptime_msg"
          ></UptimeStatus>
        </div>
        <div class="p-1">
          <small class="white-text tracking-in-expand">
            Last updated {{ convertDate(data.api?._meta?.last_updated) }}</small
          >
        </div>
      </div>
    </teleport>
    <template v-if="data.ready">
      <teleport to=".info">
        <div style="margin-top: 30px;">
          <span
            v-if="data?.api?.info?.['x-trapi']?.version"
            style="margin-left: 0px;"
            class="versionBadge pink lighten-2"
            v-text="'TRAPI ' + data?.api?.info?.['x-trapi']?.version"
          >
          </span>
          <span
            v-if="data?.api?.info?.['x-translator']?.component"
            class="versionBadge indigo darken-2"
            >Translator: {{ data?.api?.info?.['x-translator']?.component }}</span
          >
          <span
            v-if="data?.api?.tags && data?.api?.tags.some((item) => item?.name == 'biothings')"
            class="versionBadge grey darken-2"
          >
            BioThings API
          </span>
        </div>
      </teleport>
    </template>
    <div class="grey lighten-5 z-depth-3" id="swagger-ui" style="overflow: hidden"></div>
  </main>
</template>

<script>
import { reactive, onMounted, onBeforeMount, getCurrentInstance } from 'vue';
import { useRoute } from 'vue-router';
// import { useMeta } from 'vue-meta'

import SwaggerUI from 'swagger-ui';
import axios from 'axios';
import moment from 'moment';
import UptimeStatus from '../components/UptimeStatus.vue';
import SourceStatus from '../components/SourceStatus.vue';

import 'swagger-ui/dist/swagger-ui.css';

export default {
  name: 'UI',
  components: {
    SourceStatus,
    UptimeStatus
  },
  setup() {
    let data = reactive({
      apiID: '',
      name: '',
      api: Object,
      //ensure nav has mounted for teleport to work
      ready: false
    });

    const route = useRoute();
    const app = getCurrentInstance();

    // Or use a computed prop
    // const computedMeta = computed(() => ({
    //   title: 'SmartAPI | '+ data.api?.info?.title,
    //   description : data.api?.info?.description
    // }))

    // useMeta(computedMeta)

    let loadSwaggerUI = (dataurl) => {
      const HideEmptyTagsPlugin = () => {
        return {
          statePlugins: {
            spec: {
              wrapSelectors: {
                taggedOperations:
                  (ori) =>
                  (...args) => {
                    return ori(...args).filter(
                      (tagMeta) => tagMeta.get('operations') && tagMeta.get('operations').size > 0
                    );
                  }
              }
            }
          }
        };
      };

      const ui = SwaggerUI({
        url: dataurl,
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [SwaggerUI.presets.apis],
        plugins: [
          SwaggerUI.plugins.DownloadUrl,
          // plug-in to hide empty tags
          HideEmptyTagsPlugin
        ],
        onComplete: () => {
          let servers_selected = document.querySelector('div.servers label select')?.value;
          // console.log("severs", servers_selected)
          if (servers_selected) {
            if (servers_selected.includes('http:') && window.location.protocol == 'https:') {
              document
                .querySelector('div.servers label select')
                .insertAdjacentHTML(
                  'afterend',
                  '<div class="yellow lighten-4 red-text padding20"> <i class="material-icons">warning</i> Your connection is secure (HTTPS) and the selected server utilizes an insecure communication (HTTP). <br/>This will likely result in errors, please select a matching protocol server or change your connection. </div>'
                );
            }
          }
        }
      });
      window.ui = ui;
    };

    let getMetadata = (url) => {
      axios
        .get(url)
        .then((res) => {
          data.api = res.data;
        })
        .catch((err) => {
          throw err;
        });
    };

    let convertDate = (timestamp) => {
      var date = new Date(timestamp);
      date = moment(date).format('LLL');
      return date;
    };

    onMounted(() => {
      setTimeout(() => {
        data.ready = true;
      }, 2000);
      loadSwaggerUI(
        app.appContext.config.globalProperties.$apiUrl + '/metadata/' + data.apiID + '?raw=1'
      );
    });

    onBeforeMount(() => {
      data.apiID = route.params.smartapi_id;
      getMetadata(
        app.appContext.config.globalProperties.$apiUrl + '/metadata/' + data.apiID + '?raw=1'
      );
    });

    return {
      data,
      convertDate,
      status
    };
  }
};
</script>

<style scoped>
.info {
  margin: 10px;
}
</style>
