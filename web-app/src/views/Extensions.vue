<template>
  <main id="extensions" class="white w-100 p-4">
    <MetaHead title="SmartAPI | Extensions"></MetaHead>
    <div class="d-flex blue-grey-text">
      <img width="100" src="@/assets/img/spec.svg" class="responsive-img" />
      <h1 style="font-size: 2em !important">Extend your SmartAPI</h1>
    </div>
    <p>
      Extend your OpenAPI SmartAPI specification with custom properties (extensions) to make your
      project compatible with other field relevant projects.
    </p>
    <p>
      Extensions, or vendor extensions, are custom properties that start with <code>x-</code>, such
      as <code>x-logo</code>. They can be used to describe extra functionality that is not covered
      by the standard Swagger specification.
    </p>
    <p>
      <a target="_blank" href="https://swagger.io/docs/specification/2-0/swagger-extensions/"
        >Learn more about OpenAPI extensions. <i class="fa fa-external-link" aria-hidden="true"></i
      ></a>
    </p>
    <p>Currently SmartAPI supports the following extensions:</p>
    <p class="p-2 black">
      <span class="white-text">Go to:</span>
      <RouterLink
        class="m-1"
        v-for="(val, name) in extensions"
        :key="name"
        :to="{ path: '/extensions/' + name }"
      >
        <b>{{ name }} </b>
      </RouterLink>
    </p>
    <template v-for="(val, name) in view_extensions" :key="name">
      <section
        :id="name"
        class="row bottom-border d-flex align-items-center justify-content-center flex-wrap"
        style="margin-bottom: 100px"
      >
        <div class="col s12 m2">
          <img :src="val.image" width="200" :alt="name" />
        </div>
        <div class="col s12 m10 p-2">
          <h2 style="font-size: 3em !important; font-weight: 100">
            <a :href="'#' + name">{{ name }}</a>
          </h2>
          <p v-html="val.description"></p>
          <p>
            <a :href="val.link" target="_blank"
              >Learn More. <i class="fa fa-external-link" aria-hidden="true"></i
            ></a>
          </p>
        </div>
        <details class="col s12 m12 extensions-table" open>
          <summary class="blue-text p-3">
            <b class="pointer">View {{ name }} extensions ({{ val?.extensions?.length }})</b>
          </summary>
          <table class="col s12 striped responsive-table highlight">
            <thead>
              <th>Name</th>
              <th>Necessity</th>
              <th>Description</th>
              <th>Type</th>
              <th>Resources</th>
              <th>Example</th>
            </thead>
            <tbody>
              <template v-for="extension in val.extensions" :key="extension.name">
                <tr style="border-bottom: 2px solid gray !important">
                  <td>
                    <code
                      ><b>"{{ extension.name }}"</b></code
                    >
                  </td>
                  <td>
                    <span
                      v-if="extension?.necessity"
                      :class="{
                        'red white-text ': extension.necessity == 'required',
                        'blue white-text ': extension.necessity == 'optional',
                        'amber black-text': extension.necessity == 'should'
                      }"
                      class="badge rounded caps"
                    >
                      {{ extension.necessity }}</span
                    >
                  </td>
                  <td>
                    <p>
                      <small>{{ extension.description }}</small>
                    </p>
                  </td>
                  <td>
                    <span class="badge rounded grey lighten-2">{{ extension.type }}</span>
                    <div v-if="extension?.enum">
                      <ul>
                        <li
                          style="list-style: circle !important"
                          v-for="item in extension.enum"
                          :key="item"
                        >
                          <small>{{ item }}</small>
                        </li>
                      </ul>
                    </div>
                  </td>
                  <td>
                    <a
                      v-if="extension.doc_link"
                      :href="extension.doc_link"
                      target="_blank"
                      rel="nonreferrer"
                      >Docs <i class="fa fa-external-link" aria-hidden="true"></i
                    ></a>
                  </td>
                  <td class="black lime-text" style="white-space: pre">
                    <div style="overflow: scroll; max-height: 200px !important">
                      <small v-if="extension.example">
                        {{ JSON.stringify(extension.example, null, '\t') }}
                      </small>
                    </div>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </details>
      </section>
    </template>
  </main>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'Extensions',
  methods: {},
  props: ['name'],
  data: function () {
    return {
      view_extensions: {}
    };
  },
  computed: {
    ...mapGetters(['extensions'])
  },
  methods: {
    handleName: function (v) {
      if (this.extensions?.[v]) {
        let ext = {};
        ext[v] = this.extensions?.[v];
        return ext;
      } else {
        return this.extensions;
      }
    }
  },
  watch: {
    name: {
      immediate: true,
      handler: function (v) {
        this.view_extensions = this.handleName(v);
      }
    }
  }
};
</script>

<style scoped>
.extensions-table summary::marker {
  margin: auto !important;
  text-align: center;
}
#extensions section:nth-child(even) {
  background-color: rgb(240, 242, 247);
}
</style>
