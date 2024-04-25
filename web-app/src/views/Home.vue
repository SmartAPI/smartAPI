<template>
  <main id="index-app">
    <MetaHead title="SmartAPI | Home"></MetaHead>
    <div class="section mainBackgroundParticle heroContainer" id="index-banner">
      <vue-particles
        id="tsparticles"
        :particlesInit="particlesInit"
        :particlesLoaded="particlesLoaded"
        :options="{
          fullScreen: false,
          background: {
            color: {
              value: 'transparent'
            }
          },
          fpsLimit: 120,
          interactivity: {
            events: {
              onClick: {
                enable: true,
                mode: 'push'
              },
              resize: true
            },
            modes: {
              bubble: {
                distance: 400,
                duration: 2,
                opacity: 0.8,
                size: 40
              },
              push: {
                quantity: 2
              }
            }
          },
          particles: {
            color: {
              value: '#ffffff'
            },
            links: {
              color: '#ffffff',
              distance: 150,
              enable: true,
              opacity: 1,
              width: 1
            },
            move: {
              direction: 'none',
              enable: true,
              outMode: 'bounce',
              random: false,
              speed: 0.5,
              straight: false
            },
            number: {
              density: {
                enable: true,
                area: 800
              },
              value: 80
            },
            opacity: {
              value: 1
            },
            shape: {
              type: 'circle'
            },
            size: {
              random: true,
              value: 5
            }
          },
          detectRetina: true
        }"
      />
      <div class="center-align indexChild container p-2">
        <img
          src="@/assets/img/logo-small.svg"
          width="40%"
          alt="SmartAPI Logo"
          class="hide-on-med-only hide-on-large-only"
        />
        <img
          src="@/assets/img/logo-medium.svg"
          width="60%"
          alt="SmartAPI Logo"
          class="hide-on-small-only hide-on-large-only"
        />
        <img
          src="@/assets/img/logo-large.svg"
          width="100%"
          alt="SmartAPI Logo"
          class="hide-on-small-only hide-on-med-only"
          :style="{ maxWidth: '500px' }"
        />
        <h1
          class="white-text logoFont lighter hide-on-small-only textShadow"
          style="margin: 5px; font-size: 10vw !important"
        >
          Smart<span class="blue-text">API</span>
        </h1>
        <h1
          style="font-size: 18vw !important"
          class="logoFont white-text lighter show-on-small hide-on-med-and-up margin10"
        >
          SmartAPI
        </h1>
        <h2 class="black-text hide-on-small-only" style="font-weight: 200">
          BUILDING A CONNECTED NETWORK OF
          <b
            class="blue-text"
            data-tippy-content="<small>FINDABLE, ACCESSIBLE, INTEROPERABLE, AND REUSABLE</small>"
            >FAIR</b
          >
          APIS
        </h2>
        <h2 class="hide-on-med-only hide-on-large-only show-on-small black-text">
          BUILDING A CONNECTED NETWORK OF
          <b
            class="blue-text"
            data-tippy-content="<small>FINDABLE, ACCESSIBLE, INTEROPERABLE, AND REUSABLE</small>"
            >FAIR</b
          >
          APIS
        </h2>
      </div>
    </div>
    <div class="container-fluid">
      <div class="row">
        <div class="col s12">
          <div class="container d-flex align-items-center justify-content-center flex-wrap">
            <div class="col s12 m4 center">
              <img width="300" src="@/assets/img/whatis.svg" class="responsive-img" />
            </div>
            <div class="col s12 m8 p-2">
              <h3>What is SmartAPI?</h3>
              <p>
                The SmartAPI project aims to maximize the
                <a target="_blank" href="https://www.go-fair.org/fair-principles/"
                  >FAIRness <i class="fa fa-external-link" aria-hidden="true"></i
                ></a>
                (Findability, Accessibility, Interoperability, and Reusability) of web-based
                Application Programming Interfaces (APIs).
              </p>
              <p>
                Rich metadata is essential to properly describe your API so that it becomes
                discoverable, connected, and reusable. We have developed a openAPI-based
                specification for defining the key API metadata elements and value sets. SmartAPI’s
                leverage the
                <a target="_blank" href="https://swagger.io/docs/specification/about/"
                  >Open API specification v3 <i class="fa fa-external-link" aria-hidden="true"></i
                ></a>
                and JSON-LD for providing semantically annotated JSON content that can be treated as
                Linked Data.
              </p>
            </div>
          </div>
        </div>
        <div class="col s12 white-text blue-black">
          <div class="container center p-2 v-lines">
            <Egg></Egg>
            <h3><b>New to SmartAPI?</b></h3>
            <p>Becoming part of SmartAPI is a straightforward process</p>
            <p class="lime-text">
              <strong
                ><i class="fa fa-check green-text"></i>Document >
                <i class="fa fa-check green-text"></i>Register >
                <i class="fa fa-check green-text"></i>Manage and Explore</strong
              >
            </p>
            <p>
              Follow this step-by-step guide to help you contribute to SmartAPI for the first time
            </p>
            <router-link class="btn blue btn-large" to="/guide"
              >SmartAPI Guide <i class="fa fa-chevron-right"></i
            ></router-link>
          </div>
        </div>
        <div class="col s12">
          <div class="container">
            <div class="col s12 m8">
              <div class="d-flex align-items-center">
                <img
                  alt="icon"
                  class="margin10"
                  width="70"
                  src="@/assets/img/group.svg"
                  id="groupIcon"
                />
                <h3 style="font-size: 3em !important">DISCOVER</h3>
              </div>
              <p>
                The SmartAPI registry optimizes collaboration, fosters interdisciplinary synergies,
                and ultimately catalyzes discoveries and advancements in biomedical sciences.
                Researchers, developers, and healthcare professionals can navigate the SmartAPI
                registry to identify APIs that align with their specific needs, expediting the
                development of innovative tools and solutions.
              </p>
            </div>
            <div class="col s12 m4 d-flex flex-wrap p-1 justify-content-center align-items-center">
              <img width="300" src="@/assets/img/registryapis.svg" class="responsive-img" />
              <router-link class="btn blue" to="/registry"
                >Browse SmartAPI Registry <i class="fa fa-chevron-right"></i
              ></router-link>
            </div>
            <div class="border-bottom col s12"></div>
            <div class="col s12 m8">
              <div class="d-flex align-items-center">
                <img
                  alt="icon"
                  class="margin10"
                  width="70"
                  src="@/assets/img/edit.svg"
                  id="groupIcon"
                />
                <h3 style="font-size: 3em !important">DOCUMENT</h3>
              </div>
              <p>
                Use SmartAPI's own built-in editor to harness the power of
                <a target="_blank" href="https://swagger.io/docs/specification/about/"
                  >OpenAPI specification <i class="fa fa-external-link" aria-hidden="true"></i
                ></a>
                to create machine-readable documentation that offers a comprehensive blueprint of
                your API so others can understand and interact with your API without delving into
                its underlying code.
              </p>
              <p>
                Once registered, SmartAPI provides an easy-to-use dashboard so you can quickly
                update and monitor your API metadata.
              </p>
            </div>
            <div class="col s12 m4 d-flex p-1 flex-wrap justify-content-center align-items-center">
              <img width="300" src="@/assets/img/monitor.svg" class="responsive-img" />
              <router-link class="btn green" to="/editor"
                >Use the Editor <i class="fa fa-chevron-right"></i
              ></router-link>
            </div>
            <div class="border-bottom col s12"></div>
            <div class="col s12 m8">
              <div class="d-flex align-items-center">
                <img
                  alt="icon"
                  class="margin10"
                  width="70"
                  src="@/assets/img/metakg-01.svg"
                  id="groupIcon"
                />
                <h3 style="font-size: 3em !important">EXPLORE</h3>
              </div>
              <p>
                SmartAPI's MetaKG Explorer provides a targeted approach to discovering biomedical
                APIs aligned with a large variety of biological entities.
              </p>
              <p>
                This tool seeks to empower researchers to navigate the intricate landscape of life
                sciences with precision and agility.
              </p>
              <router-link
                class="purple-text"
                to="/portal/translator/metakg?size=20&subject=Disease&object=ChemicalEntity"
                >Eg. Lookup APIs that provide Disease - Chemical Entity relationships</router-link
              >
            </div>
            <div class="col s12 m4 d-flex flex-wrap p-1 justify-content-center align-items-center">
              <img width="300" src="@/assets/img/mkg.svg" class="responsive-img" />
              <router-link class="btn purple" to="/portal/translator/metakg"
                >Try MetaKG Explorer <i class="fa fa-chevron-right"></i
              ></router-link>
            </div>
          </div>
        </div>
        <div class="col s12 white-text mat-black">
          <div class="container p-4 extensions">
            <div class="d-flex justify-content-start align-items-center">
              <img width="100" src="@/assets/img/spec.svg" class="responsive-img" />
              <h2 class="textShadow"><b>Extend your SmartAPI Metadata</b></h2>
            </div>
            <div class="p-2 m-1" style="background-color: rgba(0, 0, 0, 0.6)">
              <p>
                Learn how to use OpenAPI extensions to make your specification compatible with other
                important projects in the biomedical community. Eg.
                <a target="_blank" rel="nonreferrer" href="https://explorer.biothings.io/"
                  >BioThings Explorer <i class="fa fa-external-link" aria-hidden="true"></i
                ></a>
              </p>
              <router-link class="btn green btn-large" to="/extensions"
                >View All Available Extensions <i class="fa fa-chevron-right"></i
              ></router-link>
            </div>
          </div>
        </div>
        <div class="col s12 api-back white-text">
          <div class="container">
            <div class="col s12 m6 d-flex p-1 justify-content-center align-items-center">
              <h2 style="font-size: 3em !important; font-weight: 200">
                SmartAPI has it's own API! Check it out!
              </h2>
            </div>
            <div class="col s12 m6">
              <div class="d-flex justify-content-start align-items-center">
                <img width="30" class="mr-1" src="@/assets/img/lightning.svg" />
                <h4>FAST</h4>
              </div>
              <div class="d-flex justify-content-start align-items-center">
                <img width="30" class="mr-1" src="@/assets/img/ok.svg" />
                <h4>RELIABLE</h4>
              </div>
              <div class="d-flex justify-content-start align-items-center">
                <img width="30" class="mr-1" src="@/assets/img/uptodate.svg" />
                <h4>UP-TO-DATE</h4>
              </div>
            </div>
            <div class="col s12 p-2">
              <p>
                Explore the vast array of features and functionalities provided by SmartAPI through
                its dedicated API service and take advantage of the comprehensive network of
                knowledge available within SmartAPI's API infrastructure.
              </p>
              <div class="d-flex align-items-center justify-content-center">
                <h4 class="lime-text mr-1">Try the SmartAPI API Now!</h4>
                <router-link class="btn btn-large green" to="/ui/27a5b60716c3a401f2c021a5b718c5b1"
                  >Try It!</router-link
                >
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script>
import cookie from '@/assets/img/api-cookie.svg';
import pic from '@/assets/img/network.svg';
import { loadSlim } from 'tsparticles-slim';

import Egg from '../components/Icons/Egg.vue';

export default {
  name: 'Home',
  components: { Egg },
  data: function () {
    return {
      network_img: pic
    };
  },
  methods: {
    checkCookieNotification() {
      if (!localStorage.getItem('DontShowCookies')) {
        this.$swal({
          toast: true,
          imageUrl: cookie,
          imageWidth: 120,
          width: '50vw',
          position: 'top',
          showConfirmButton: false,
          html: `<div class="center">
            <p>This website uses cookies for analytics purposes. <br/>By continuining to use this website you are giving consent to cookies being used.<br/><a class="link" target="_blank" href="/privacy">Learn more</a> about how SmartAPI uses cookies. </p>
            <button class="btn blue" id="cookieButton">Agree, Do Not Show Again</button>
            </div>`
        });

        document.getElementById('cookieButton').addEventListener('click', function () {
          localStorage.setItem('DontShowCookies', 'true');
          this.$swal.close();
        });
      }
    },
    async particlesInit(engine) {
      await loadSlim(engine);
    },
    async particlesLoaded() {
      console.log('Particles container loaded');
    }
  },
  mounted: function () {
    this.checkCookieNotification();
  }
};
</script>

<style lang="css" scoped>
#tsparticles {
  height: 50vh;
  min-height: 50vh;
  max-height: 864px;
}
p.blue-grey-text {
  font-size: 1.3em;
}
.heroContainer {
  overflow: hidden;
  padding-top: 200px;
}
</style>
