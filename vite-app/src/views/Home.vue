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
              opacity: 0.5,
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
              value: 0.5
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
      <div class="center-align indexChild container">
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
        <h3
          class="white-text logoFont lighter hide-on-small-only textShadow"
          style="margin: 5px; font-size: 10vw !important"
        >
          Smart<span class="l-blue-text">API</span>
        </h3>
        <h3
          style="font-size: 18vw !important"
          class="logoFont white-text lighter show-on-small hide-on-med-and-up margin10 textShadow"
        >
          SmartAPI
        </h3>
        <h5 class="white-text hide-on-small-only" style="font-weight: 100">
          BUILDING A CONNECTED NETWORK OF FAIR APIS
        </h5>
        <h5 class="hide-on-med-only hide-on-large-only show-on-small l-blue-text">
          BUILDING A CONNECTED NETWORK OF FAIR APIS
        </h5>
      </div>
    </div>
    <!-- new to SmartAPI-->
    <div class="blue-grey darken-4" style="overflow: hidden; padding: 50px 10px">
      <div class="container-fluid center white-text padding20">
        <h5 class="shine">New to <span class="logoFont">SmartAPI</span>?</h5>
        <p class="lighter">
          Follow this step-by-step guide to help you contribute to SmartAPI for the first time
        </p>
        <br />
        <router-link to="/guide" class="clearButton">Start Here</router-link>
      </div>
    </div>

    <div id="intro1" class="section grey lighten-5" :style="{ paddingBottom: '0px !important' }">
      <div class="container">
        <div class="row">
          <div class="col l4 m4">
            <object id="whatIs" width="200" :data="network_img" />
          </div>
          <div class="col l8 m8">
            <h2
              class="center hide-on-small-only header blue-grey-text lighter flow-text hide-on-small-only"
            >
              What is a <span class="logoFont blue-text">SmartAPI</span>?
            </h2>
            <div class="col s12 center-align hide-on-med-and-up show-on-small padding20">
              <Image img_width="40%" img_name="logo-medium.svg" class="responsive-img"></Image>
            </div>
            <h3 class="center hide-on-med-and-up show-on-small">
              What is a <span class="logoFont blue-grey-text">SmartAPI</span>?
            </h3>
            <p class="blue-grey-text flow-text">
              The SmartAPI project aims to maximize the FAIRness (Findability, Accessibility,
              Interoperability, and Reusability) of web-based Application Programming Interfaces
              (APIs). Rich metadata is essential to properly describe your API so that it becomes
              discoverable, connected, and reusable. We have developed a
              <a href="http://openapis.org" target="_blank"></a>openAPI-based
              <a
                href="https://github.com/SmartAPI/smartAPI-Specification/blob/OpenAPI.next/versions/3.0.0.md"
                target="_blank"
              >
                specification</a
              >
              for defining the key API metadata elements and value sets. SmartAPI's leverage the
              <a href="https://www.openapis.org/" target="_blank">Open API specification v3 </a> and
              <a href="http://json-ld.org" target="_blank">JSON-LD</a> for providing semantically
              annotated JSON content that can be treated as
              <a href="http://linkeddata.org/" target="_blank">Linked Data</a>.
            </p>
          </div>
        </div>
      </div>

      <div style="margin-bottom: 0px" id="topicsBox" class="row blue-grey">
        <div class="col s12 m6 l4 center-align padding20 topic" id="registryBox">
          <img
            alt="icon"
            class="margin10"
            width="70"
            src="@/assets/img/search.svg"
            id="registryIcon"
          />
          <br />
          <router-link to="/registry" class="clearButton">Registry</router-link>
          <p class="l-blue-text">Search the registry of SmartAPIs</p>
        </div>
        <div class="col s12 m6 l4 center-align padding20 topic" id="editBox">
          <img alt="icon" class="margin10" width="70" src="@/assets/img/edit.svg" id="editIcon" />
          <br />
          <router-link to="/editor" class="clearButton">Editor</router-link>
          <p class="l-blue-text">Author your own SmartAPI metadata</p>
        </div>
        <div class="col s12 m6 l4 center-align padding20 topic" id="apiBox">
          <img alt="icon" class="margin10" width="70" src="@/assets/img/api.svg" id="apiIcon" />
          <br />
          <router-link to="/ui/27a5b60716c3a401f2c021a5b718c5b1" class="clearButton"
            >API</router-link
          >
          <p class="l-blue-text">Learn about and access the SmartAPI services</p>
        </div>
        <div class="col s12 m6 l4 center-align padding20 topic" id="specBox">
          <img alt="icon" class="margin10" width="70" src="@/assets/img/spec.svg" id="specIcon" />
          <br />
          <a
            class="clearButton"
            target="_blank"
            href="https://github.com/SmartAPI/smartAPI-Specification/blob/OpenAPI.next/versions/3.0.0.md"
            >Specification</a
          >
          <p class="l-blue-text">SmartAPI metadata specification to start your API</p>
        </div>
        <div class="col s12 m6 l4 center-align padding20 topic" id="guideBox">
          <img alt="icon" class="margin10" width="70" src="@/assets/img/guide.svg" id="guideIcon" />
          <br />
          <router-link to="/guide" class="clearButton">Guide</router-link>
          <p class="l-blue-text">Contribute to SmartAPI for the first time</p>
        </div>
        <div class="col s12 m6 l4 center-align padding20 topic" id="groupBox">
          <img alt="icon" class="margin10" width="70" src="@/assets/img/group.svg" id="groupIcon" />
          <br />
          <a href="https://goo.gl/D4e0xL" target="_blank" class="clearButton">Working Group</a>
          <p class="l-blue-text">Join the API Interoperability working group</p>
        </div>
      </div>
      <div class="section grey lighten-4" id="intro2">
        <div class="container">
          <div class="row">
            <div class="col l8 s12 m8">
              <h2 class="center header blue-grey-text text_h2 flow-text hide-on-small-only">
                Why do we need <span class="logoFont">SmartAPI</span>s?
              </h2>
              <!-- content for small screen only -->
              <div class="col s12 center-align hide-on-med-and-up show-on-small padding20">
                <img alt="image" width="70%" class="responsive-img" src="@/assets/img/graph.jpg" />
              </div>
              <h3 class="center hide-on-med-and-up show-on-small">
                Why do we need <span class="logoFont blue-grey-text">SmartAPI</span>s?
              </h3>
              <p class="blue-grey-text">
                Data analysis is increasingly being performed using cloud-based, web-friendly
                application programming interfaces (APIs). Thousands of tools and APIs are available
                through web service registries such as
                <a href="http://www.programmableweb.com/" target="_blank">Programmable Web</a>,
                <a href="https://www.biocatalogue.org/" target="_blank">BioCatalogue</a> and cloud
                platforms such as <a href="https://galaxyproject.org/" target="_blank">Galaxy</a>.
                Searching these and other API repositories to find a set of tools to retrieve or
                operate on data of interest presents a number of formidable challenges: users must
                not only supply the right combination of search terms, but must also closely examine
                the API outputs to determine whether they can be connected together. SmartAPIs
                tackle this challenge because they contain the rich metadata needed to precisely
                describe the service and the data that it operates on or provides.
              </p>
            </div>
            <div class="col s12 l4 center-align padding20 hide-on-small-only m4">
              <img
                alt="image"
                width="100%"
                class="responsive-img introPic circle"
                src="@/assets/img/graph.jpg"
              />
            </div>
          </div>
        </div>
      </div>

      <div class="section" id="intro3">
        <div class="container">
          <div class="row">
            <div class="col l4 s12 center-align padding20 hide-on-small-only m4">
              <img
                alt="image2"
                width="100%"
                class="responsive-img introPic circle"
                src="@/assets/img/strand.jpg"
              />
            </div>
            <div class="col l8 s12 m8">
              <h2 class="center header blue-grey-text text_h2 flow-text hide-on-small-only">
                What does the <span class="logoFont">SmartAPI</span> offer?
              </h2>
              <!-- content for small screen only -->
              <div class="col s12 center-align hide-on-med-and-up show-on-small padding20">
                <img width="70%" class="responsive-img" src="@/assets/img/strand.jpg" />
              </div>
              <h3 class="center hide-on-med-and-up show-on-small">
                What does the <span class="logoFont blue-grey-text">SmartAPI</span> offer?
              </h3>
              <p class="blue-grey-text">
                Richly annotated APIs will provide the assets by which users will be able to search,
                browse, query, and reuse APIs. Users and intelligent agents being able to traverse a
                highly connected network of smartAPIs. Users will be able to automatically find APIs
                whose outputs are the inputs for other services. Ultimately, we envision the
                automatic generation of workflows that take users to where they want to go with what
                they have today.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script>
// @ is an alias to /src
// import Vivus from 'vivus'
import cookie from '@/assets/img/api-cookie.svg'
import pic from '@/assets/img/network.svg'
import { loadSlim } from 'tsparticles-slim'

// const particlesInit = async engine => {
//     //await loadFull(engine);
//     await loadSlim(engine);
// };

// const particlesLoaded = async container => {
//     console.log("Particles container loaded", container);
// };

export default {
  name: 'Home',
  data: function () {
    return {
      network_img: pic
    }
  },
  methods: {
    checkCookieNotification() {
      if (!localStorage.getItem('DontShowCookies')) {
        this.$swal({
          toast: true,
          imageUrl: cookie,
          imageWidth: 200,
          width: '90vw',
          position: 'top',
          showConfirmButton: false,
          html: '<p>This website uses cookies for analytics purposes. <br/>By continuining to use this website you are giving consent to cookies being used.<br/><a class="link" target="_blank" href="/privacy">Learn more</a> about how SmartAPI uses cookies. </p><button class="btn blue" id="cookieButton">Agree, Do Not Show Again</button> '
        })

        document.getElementById('cookieButton').addEventListener('click', function () {
          localStorage.setItem('DontShowCookies', 'true')
          this.$swal.close()
        })
      }
    },
    async particlesInit(engine) {
      await loadSlim(engine)
    },
    async particlesLoaded() {
      console.log('Particles container loaded')
    }
  },
  mounted: function () {
    // new Vivus('whatIs', { duration: 200, type: 'oneByOne' })
    this.checkCookieNotification()
  }
}
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
}
</style>
