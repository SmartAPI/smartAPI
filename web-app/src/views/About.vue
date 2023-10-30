<template>
  <main id="about-app" class="white" style="width: 100%">
    <MetaHead title="SmartAPI | About"></MetaHead>
    <section class="container center padding20">
      <img
        width="40%"
        src="@/assets/img/logo-small-text.svg"
        class="hide-on-med-only hide-on-large-only"
      />
      <img
        width="45%"
        src="@/assets/img/logo-medium-text.svg"
        class="hide-on-small-only hide-on-large-only"
      />
      <img
        width="50%"
        src="@/assets/img/logo-large-text.svg"
        class="hide-on-small-only hide-on-med-only"
        :style="{ maxWidth: '600px' }"
      />
      <h3 class="blue-text flow-text bold">BUILDING A CONNECTED NETWORK OF FAIR APIS</h3>
      <p class="blue-grey-text flow-text">
        The SmartAPI project aims to maximize the FAIRness of web-based Application Programming
        Interfaces (APIs). Rich metadata is essential to properly describe your API so that it
        becomes discoverable, connected, and reusable. We have developed a openAPI-based
        specification for defining the key API metadata elements and value sets. SmartAPI's leverage
        the <a href="https://www.openapis.org/" target="_blank">Open API</a> specification v3 and
        <a href="https://json-ld.org/" target="_blank">JSON-LD</a> for providing semantically
        annotated JSON content that can be treated as Linked Data.
      </p>
      <p class="blue-grey-text flow-text">
        All of the API metadata available from the SmartAPI registry is FAIR too.
        <a href="https://fairsharing.org/biodbcore-001171/" target="_blank">Learn more.</a>
      </p>
    </section>

    <section class="container center padding20">
      <h2 class="blue-text flow-text bold">What is FAIR?</h2>
      <table class="fairTable">
        <tbody>
          <tr>
            <td>
              <span class="fair">F</span>
            </td>
            <td>
              <p class="blue-grey-text flow-text">
                <b>Findable:</b> The first step in (re)using data is to find it. Metadata and data
                should be easy to find for both humans and computers. Machine-readable metadata are
                essential for automatic discovery of datasets and services, so this is an essential
                component of the FAIRification process.
              </p>
            </td>
          </tr>
          <tr>
            <td>
              <span class="fair">A</span>
            </td>
            <td>
              <p class="blue-grey-text flow-text">
                <b>Accessible:</b> Once the user finds the required data, she/he needs to know how
                can they be accessed, possibly including authentication and authorization.
              </p>
            </td>
          </tr>
          <tr>
            <td>
              <span class="fair">I</span>
            </td>
            <td>
              <p class="blue-grey-text flow-text">
                <b>Interoperable:</b> The data usually need to be integrated with other data. In
                addition, the data need to interoperate with applications or workflows for analysis,
                storage, and processing.
              </p>
            </td>
          </tr>
          <tr>
            <td>
              <span class="fair">R</span>
            </td>
            <td>
              <p class="blue-grey-text flow-text">
                <b>Reusable:</b> The ultimate goal of FAIR is to optimise the reuse of data. To
                achieve this, metadata and data should be well-described so that they can be
                replicated and/or combined in different settings.
              </p>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <section class="container center padding20">
      <h2 class="blue-text flow-text bold">Team</h2>
      <div class="contributor-container">
        <template v-for="(organization, org_index) in contributors" :key="org_index">
          <template v-if="organization.members.length">
            <div class="center padding20 hide-on-small-only" style="width: 100%">
              <h3 v-if="organization.name" class="blue-text">{{ organization.name }}</h3>
              <img v-else :src="organization.image" width="400" :alt="organization.name" />
            </div>
            <template v-for="person in organization.members" :key="person.name">
              <div
                href="javascript:void(0)"
                class="contributor-box contributor modal-trigger"
                @click="popUpDetails(person)"
              >
                <img
                  class="circle scale-in-center squarePic"
                  width="70%"
                  :src="person.image"
                  :alt="person.name"
                />
                <p class="bold blue-text">{{ person.name }} {{ person.lastname }}</p>
                <p class="blue-grey-text smallFont">{{ person.title }}</p>
                <img
                  class="hide-on-med-only hide-on-large-only"
                  :src="person.work_logo"
                  width="100%"
                  alt="logo"
                />
              </div>
            </template>
          </template>
        </template>
      </div>
      <div class="col-sm-12">
        <h5 class="flow-text bold blue-text">
          NIH Data Commons API Interoperability Working Group
        </h5>
        <ul>
          <li v-for="(person, i) in otherMembers" :key="i">
            <span class="blue-text">{{ person.name }}</span
            >, {{ person.organization }}
          </li>
        </ul>
      </div>
    </section>

    <VModal v-model="showModal" @confirm="showModal = false">
      <template v-slot:title>{{ 'About ' + selectedPerson.name || 'About' }}</template>
      <div v-if="selectedPerson" class="white row p-1">
        <div class="col s12 m4 l4">
          <div>
            <img
              class="circle aboutPic"
              :style="{ width: '80%' }"
              :src="selectedPerson.image"
              :alt="selectedPerson.name"
            />
            <p>
              <template v-for="link in selectedPerson.links" :key="link">
                <a
                  v-if="link.href.length > 1"
                  :href="link.href"
                  target="_blank"
                  class="social-icon"
                >
                  <i
                    v-if="link.title === 'twitter'"
                    class="fa fa-twitter-square fa-3x"
                    aria-hidden="true"
                  ></i>
                  <i
                    v-if="link.title === 'linkedin'"
                    class="fa fa-linkedin-square fa-3x"
                    aria-hidden="true"
                  ></i>
                  <i
                    v-if="link.title === 'github'"
                    class="fa fa-github-square fa-3x"
                    aria-hidden="true"
                  ></i>
                </a>
              </template>
            </p>
          </div>
          <p class="grey-text smallFont">
            Search SmartAPI for contributions by {{ selectedPerson.name }}
            {{ selectedPerson.lastname }}<br />
            <router-link
              class="btn blue smallFont margin20"
              :to="'/registry?q=' + selectedPerson.name + ' ' + selectedPerson.lastname"
              ><i class="fa fa-search" aria-hidden="true"></i> Search</router-link
            >
          </p>
        </div>
        <div class="col s12 m8 l8">
          <p>
            <span style="font-size: 2em" class="blue-text bold"
              >{{ selectedPerson.name }} {{ selectedPerson.lastname }}</span
            >
            <span class="grey-text">/ {{ selectedPerson.title }}</span>
          </p>
          <a :href="selectedPerson.work_website" target="_blank">
            <img :src="selectedPerson.work_logo" width="200" :alt="selectedPerson.work_logo" />
          </a>
          <hr />
          <h5>About</h5>
          <p
            class="left-align blue-grey-text"
            style="font-size: 0.9em; border-left: #e4e4e4 solid 2px; padding: 10px"
            v-html="compiledMarkdown(selectedPerson.bio || '')"
          ></p>
          <p>
            <a :href="selectedPerson.personal_site" target="_blank"
              >More About {{ selectedPerson.name }}
              <i class="fa fa-external-link" aria-hidden="true"></i
            ></a>
          </p>
          <hr />
          <h5>Education</h5>
          <ul class="collection">
            <template v-for="item in selectedPerson.education" :key="item">
              <li class="collection-item">
                <i class="fa fa-university blue-text" aria-hidden="true"></i> {{ item }}
              </li>
            </template>
          </ul>
        </div>
      </div>
    </VModal>

    <section class="blue center" style="padding: 20px 10%">
      <h2 class="white-text flow-text bold">
        <i class="fa fa-trophy" aria-hidden="true"></i> Funding Support
      </h2>
      <p class="white-text padding20 flow-text">
        The SmartAPI project was started in 2015 via the support of a BD2K (Big Data to Knowledge)
        supplementary grant awarded to Drs. Michel Dumontier and Chunlei Wu. It's currently
        supported by the
        <a class="underlined white-text" href="https://ncats.nih.gov/translator" target="_blank"
          >Biomedical Data Translator program from NCATS (National Center for Advancing
          Translational Sciences)</a
        >.
      </p>
    </section>
  </main>
</template>

<script>
import { marked } from 'marked';
import { mapGetters } from 'vuex';

export default {
  components: {},
  name: 'About',
  data: function () {
    return {
      showModal: false,
      selectedPerson: {}
    };
  },
  methods: {
    popUpDetails: function (person) {
      this.showModal = true;
      this.selectedPerson = person;
    },
    compiledMarkdown: function (mdtext) {
      return marked(mdtext);
    }
  },
  computed: {
    ...mapGetters(['contributors', 'otherMembers'])
  }
};
</script>

<style lang="css" scoped>
.social-icon {
  margin-right: 5px;
}
.modal-container {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
