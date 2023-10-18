<template>
  <main class="white">
    <!-- MAIN SECTIONS -->
    <MetaHead title="SmartAPI | Translator"></MetaHead>
    <section class="center grey lighten-3 d-flex justify-content-around padding20 flex-wrap">
      <div class="row d-flex justify-content-center flex-wrap" style="align-items: stretch">
        <div class="col s12 m4 d-flex justify-content-center align-items-center">
          <Image img_name="TranslatorLogo.jpg" img_height="77px"></Image>
        </div>
        <div class="col s12 m4">
          <h1 class="blue-text bold flow-text">
            A SmartAPI Portal for NCATS Biomedical Data Translator
          </h1>
          <p class="blue-grey-text">
            This program focuses on building tools for massive knowledge integration in support of
            biomedical and translational science.
            <a target="_blank" rel="noreferrer" href="https://ncats.nih.gov/translator"
              >Learn more</a
            >
          </p>
        </div>
        <div class="col s12 m4 d-flex justify-content-center align-items-center">
          <Image img_name="ncats-logo-1.png" img_height="77"></Image>
        </div>
      </div>
      <div class="d-flex justify-content-center align-items-center flex-wrap">
        <div class="col s12 padding20 center-align fade-in">
          <Image img_name="icon-registry.svg" img_width="100px" alt="registry"></Image>
          <p>Browse registry of Translator APIs</p>
          <router-link to="/registry/translator" class="btn green">Registry</router-link>
        </div>
        <div class="col s12 padding20 center-align fade-in">
          <Image img_name="icon-summary.svg" img_width="100px" alt="summary"></Image>
          <p>View a summary of Translator APIs</p>
          <router-link to="/portal/translator/summary" class="btn green">Summary</router-link>
        </div>
        <div class="col s12 padding20 center-align fade-in">
          <Image img_name="icon-metakg.svg" img_width="100px" alt="metakg"></Image>
          <p>Explore Translator Knowledge Graph</p>
          <router-link to="/portal/translator/metakg" class="btn green">MetaKG</router-link>
        </div>
      </div>
    </section>

    <div class="d-flex align-items-stretch row flex-wrap m-0">
      <!-- Left -->
      <div class="col s12 m6 padding20">
        <h3 class="center blue-text bold">BUILD A TRANSLATOR KNOWLEDGE PROVIDER API</h3>
        <section>
          <div class="d-flex">
            <h5 class="meta_grad" style="margin-right: 5px; padding: 2px"></h5>
            <h5 class="meta_grad" style="margin-right: 5px; padding: 4px"></h5>
            <h5 class="white-text meta_grad rounded-right padding20">
              <i class="material-icons">filter_1</i> Create a Knowledge Provider API
            </h5>
          </div>
          <p class="center">
            <Image img_name="build_api-01.svg" img_width="100px" alt="create api"></Image>
          </p>
          <p>
            To create a Knowledge Provider (KP) API that's ready to be integrated into the
            Translator ecosystem, you can:
          </p>
          <ul>
            <li>
              <i class="material-icons green-text">done</i> Build a REST API with JSON output (use
              your own preferred structure).
            </li>
            <li>
              <i class="material-icons green-text">done</i> Build a ReasonerStdAPI, follow the
              instructions
              <a
                target="_blank"
                rel="noreferrer"
                href="https://github.com/NCATS-Tangerine/NCATS-ReasonerStdAPI"
                >here <i class="fa fa-external-link-square" aria-hidden="true"></i></a
              >.
            </li>
          </ul>
          <p>
            Regardless the type of APIs you are implementing, we recommend to follow these
            <a class="green-text" href="javascript:void(0)" @click="handleModal('best-practices')"
              >API best-practices</a
            >.
          </p>
          <p>
            <b>Tip: </b>You may consider using
            <a href="https://docs.biothings.io/en/latest/" target="_blank" rel="noreferrer"
              >BioThings SDK <i class="fa fa-external-link-square" aria-hidden="true"></i
            ></a>
            to build your KP APIs. BioThings SDK will create a high-quality APIs following all these
            best-practices by default. If you need the help, please
            <a href="mailto:biothings@googlegroups.com">contact</a> BioThings team (aka "Service
            Provider" KP team in Translator).
          </p>
        </section>
        <section>
          <div class="d-flex">
            <h5 class="meta_grad" style="margin-right: 5px; padding: 2px"></h5>
            <h5 class="meta_grad" style="margin-right: 5px; padding: 4px"></h5>
            <h5 class="white-text meta_grad rounded-right padding20">
              <i class="material-icons">filter_2</i> Document your API with metadata
            </h5>
          </div>
          <p class="center">
            <Image img_name="navigate_api-01.svg" img_width="100px" alt="document api"></Image>
          </p>
          <p>
            To take full advantage of SmartAPI and make your KP API compatible with Meta-KG you will
            need to:
          </p>
          <ul>
            <li>
              <i class="material-icons green-text">done</i> Create your API metadata following the
              latest
              <a href="http://spec.openapis.org/oas/v3.0.3" target="_blank" rel="noreferrer"
                >OpenAPI v3 API specification
                <i class="fa fa-external-link-square" aria-hidden="true"></i
              ></a>
            </li>
            <li>
              <i class="material-icons green-text">done</i> Add semantics of your API's inputs and
              outputs using the SmartAPI extensions.
              <a class="green-text" href="javascript:void(0)" @click="handleModal('semantic-io')"
                >Learn more</a
              >.
            </li>
          </ul>
          <p>
            You can use this <router-link to="/editor">editor</router-link> build to write/edit your
            API metadata. You can start with an existing metadata example from
            <a
              target="_blank"
              rel="noreferrer"
              href="https://github.com/NCATS-Tangerine/translator-api-registry/blob/master/mygene.info/openapi_minimum.yml"
              >mygene.info</a
            >
            API. The editor automatically validates your API metadata and gives a live preview of
            auto-generated API documentation.
          </p>
          <p>
            This guide can also <router-link to="/guide">guide</router-link> through the
            process/tools on how to create your OpenAPI v3 API metadata or how to upgrade an
            existing Swagger v2 API metadata to OpenAPI v3.
          </p>
        </section>
        <section>
          <div class="d-flex">
            <h5 class="meta_grad" style="margin-right: 5px; padding: 2px"></h5>
            <h5 class="meta_grad" style="margin-right: 5px; padding: 4px"></h5>
            <h5 class="white-text meta_grad rounded-right padding20">
              <i class="material-icons">filter_3</i> Register your API
            </h5>
          </div>
          <p>
            Once you are ready and <router-link to="/add-api">register</router-link> your KP API it
            will be listed on the
            <router-link to="/registry/translator">SmartAPI registy</router-link> and your API will
            be visible to other users. Eg.
            <router-link to="/registry?q=59dce17363dce279d389100834e43648"
              >MyGene.info API</router-link
            >
          </p>
          <p>
            The registry provides useful information and operation documentation, API status,
            editing tools and many other neat features!
          </p>
          <div class="center">
            <Image alt="registry pluses" img_name="registry_plus-01.png" img_width="90%"></Image>
          </div>
          <div class="center">
            <router-link class="btn blue btn-large" to="/registry/translator">Registry</router-link>
          </div>
        </section>
      </div>
      <!-- Right -->
      <div class="col s12 m6 padding20 meta_grad white-text container">
        <div class="center">
          <h3 class="center cyan-text bold">EXPLORE THE TRANSLATOR API META KNOWLEDGE GRAPH</h3>
          <img />
          <Image img_name="metakg-01.png" img_width="150px"></Image>
          <h1>META-KG</h1>
          <p class="center">
            <router-link class="btn green btn-large" to="/portal/translator/metakg"
              >Try it</router-link
            >
          </p>
        </div>
        <p>
          The SmartAPI Meta Knowledge Graph (Meta-KG) represents how biomedical concepts can be
          connected through APIs. Each node in the meta-KG represents a biolink entity type, e.g.
          Gene, SequenceVariant, ChemicalSubstance. Each edge in the meta-KG represents a unique
          combination of a biolink predicate, e.g. targets, treats, and an API which delivers the
          association.
        </p>
        <div class="center">
          <Image img_name="metaex.png" width="200px" alt="query example"></Image>
          <hr />
          <small>Disease affets Gene</small>
        </div>
        <p>
          The Meta-KG is constructed using the collection of SmartAPI specifications currently
          registered in SmartAPI. All APIs registered with
          <a href="https://x-bte-extension.readthedocs.io/" target="_blank" rel="nonreferrer"
            >x-bte <i class="fa fa-external-link" aria-hidden="true"></i
          ></a>
          field will be integrated into the meta-KG. In addition, all ReasonerStdAPIs registered in
          SmartAPI and implemented the /predicate endpoint will also be integrated.
        </p>
        <h5 class="bold center">What can you do with Meta-KG?</h5>
        <p>
          Traverse a complex network of connected KP APIS and search APIs based on meta-kg
          operations (API endpoints that fetch results given a desired output, input, predicate or
          any combination of them ).
        </p>
        <h4 class="cyan-text center">Example</h4>
        <div class="white grey-text rounded center p-1">
          <p>Find APIs that report entities that <b>AFFECT</b> <b>GENES</b>...</p>
        </div>
        <p>
          Meta-KG would then find all connections with <i>predicate</i> “affects” and
          <i>object</i> “Gene” and give you a list of APIs which can give you that type of results.
          <router-link to="/portal/translator/metakg?predicate=affects&object=Gene"
            >View example</router-link
          >
        </p>
        <Image
          img_name="graph_example.jpg"
          img_width="100%"
          alt="graph example"
          class="rounded"
        ></Image>
        <p class="center">
          <router-link class="btn green btn-large" to="/portal/translator/metakg"
            >Try it</router-link
          >
        </p>
      </div>
    </div>

    <VModal v-model="showModal">
      <template v-slot:title>Read Me</template>
      <MarkDown :url="mdURL" :editLink="editLink" :key="mdURL"></MarkDown>
    </VModal>
  </main>
</template>

<script>
import MarkDown from '../components/MarkDown.vue'

export default {
  name: 'TranslatorHome',
  data: function () {
    return {
      editLink: '',
      showModal: false,
      mdURL: ''
    }
  },
  components: {
    MarkDown
  },
  methods: {
    handleModal(anchor) {
      var self = this
      switch (anchor) {
        case 'best-practices':
          self.showModal = true
          self.mdURL =
            'https://raw.githubusercontent.com/SmartAPI/smartAPI/master/docs/CREATE_API.md'
          self.editLink = 'https://github.com/SmartAPI/smartAPI/edit/master/docs/CREATE_API.md'
          break
        case 'semantic-io':
          self.showModal = true
          self.mdURL =
            'https://raw.githubusercontent.com/SmartAPI/smartAPI/master/docs/API_METADATA.md'
          self.editLink = 'https://github.com/SmartAPI/smartAPI/edit/master/docs/API_METADATA.md'
          break
        default:
          console.log('no match')
      }
    }
  }
}
</script>
