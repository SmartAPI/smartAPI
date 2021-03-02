<template>
  <main id="index-app">
    <div class="section mainBackgroundParticle heroContainer" id="index-banner">
      <div id="particles-js">
        <div class="center-align indexChild container" >
            <Image img_width="40%" img_name="logo-small.svg" class="hide-on-med-only hide-on-large-only"></Image>
            <Image img_width="60%" img_name="logo-medium.svg" class="hide-on-small-only hide-on-large-only"></Image>
            <Image img_width="100%" img_name="logo-large.svg" class="hide-on-small-only hide-on-med-only" :style="{maxWidth: '500px'}"></Image>
            <h3 class="white-text logoFont lighter hide-on-small-only textShadow" style="margin:5px; font-size: 10vw !important;">Smart<span class="l-blue-text ">API</span></h3>
            <h3 style="font-size: 18vw !important;" class="logoFont white-text lighter show-on-small hide-on-med-and-up margin10 textShadow">SmartAPI</h3>
            <h5 class="white-text hide-on-small-only" style="font-weight: 100;">BUILDING A CONNECTED NETWORK OF FAIR APIS</h5>
            <h5 class="hide-on-med-only hide-on-large-only show-on-small l-blue-text">
              BUILDING A CONNECTED NETWORK OF FAIR APIS
            </h5>
        </div>
      </div>
    </div>
    <!-- new to SmartAPI-->
    <div class="whiteBack" style="overflow: hidden;">
      <div class="container-fluid center blue-grey darken-4 white-text padding20">
        <h5 class="shine">New to <span class="logoFont">SmartAPI</span>?</h5>
        <p class="lighter">
          Follow this step-by-step guide to help you contribute to SmartAPI for the first time
        </p>
        <br />
        <a class="clearButton" href="/guide">Start Here</a>
      </div>
    </div>

    <div id="intro1" class="section grey lighten-5" :style="{paddingBottom:'0px !important'}">
        <div class="container">
          <div class="row">
            <div class="col l4 m4">
              <Image id="whatIs" img_name="network.svg"></Image>
            </div>
            <div class="col l8 m8">
              <h2 class="center hide-on-small-onlyter header blue-grey-text lighter flow-text hide-on-small-only">What is a <span class="logoFont blue-text">SmartAPI</span>?</h2>
              <div class="col s12 center-align hide-on-med-and-up show-on-small padding20">
                  <Image img_width='40%' img_name="logo-medium.svg" class="responsive-img"></Image>
              </div>
              <h3 class="center hide-on-med-and-up show-on-small">What is a <span class="logoFont blue-grey-text">SmartAPI</span>?</h3>
              <p class="blue-grey-text flow-text">
                  The SmartAPI project aims to maximize the FAIRness (Findability, Accessibility, Interoperability, and Reusability) of web-based Application Programming Interfaces (APIs). Rich metadata is essential to properly describe your API so that it becomes discoverable, connected, and reusable. We have developed a <a href="http://openapis.org" target="_blank"></a>openAPI-based <a href="https://github.com/SmartAPI/smartAPI-Specification/blob/OpenAPI.next/versions/3.0.0.md" target="_blank"> specification</a> for defining the key API metadata elements and value sets. SmartAPI's leverage the <a href="https://www.openapis.org/" target="_blank">Open API specification v3 </a> and <a href="http://json-ld.org" target="_blank">JSON-LD</a> for providing semantically annotated JSON content that can be treated as <a href="http://linkeddata.org/" target="_blank">Linked Data</a>.
              </p>
            </div>
          </div>
      </div>

    <div style="margin-bottom:0px;" id="topicsBox" class="row blue-grey">

        <div class="col s12 m6 l4 center-align padding20 topic" id="registryBox" @mouseenter="animatedIcons('registryIcon')">
            <a href="/registry" >
                <Image alt="icon" class="margin10" img_width="70px" img_name="search.svg" id="registryIcon"></Image>
                <br>
                <h4 style="text-decoration: underline; text-transform: uppercase;" class="hide-on-med-and-up show-on-small white-text">Registry</h4>
                <span class="clearButton hide-on-small-only">Registry</span>
            </a>
            <p class="l-blue-text" >
                Search the registry of SmartAPIs
            </p>
        </div>
        <div class="col s12 m6 l4 center-align padding20 topic" id="editBox" @mouseenter="animatedIcons('editIcon')">
            <a href="/editor" >
                <Image alt="icon" class="margin10" img_width="70px" img_name="edit.svg" id="editIcon"></Image>
                <br>
                <h4 style="text-decoration: underline; text-transform: uppercase;" class="hide-on-med-and-up show-on-small white-text">Editor</h4>
                <span class="clearButton hide-on-small-only">Editor</span>
          </a>
            <p class="l-blue-text" >
                Author your own SmartAPI metadata
            </p>
        </div>
        <div class="col s12 m6 l4 center-align padding20 topic" id="apiBox" @mouseenter="animatedIcons('apiIcon')">
            <a href="/ui/27a5b60716c3a401f2c021a5b718c5b1" >
                <Image alt="icon" class="margin10" img_width="70px" img_name="api.svg" id="apiIcon"></Image>
                <br>
                <h4 style="text-decoration: underline; text-transform: uppercase;" class="hide-on-med-and-up show-on-small white-text">API</h4>
                <span class="clearButton hide-on-small-only">API</span>
          </a>
            <p class="l-blue-text" >
                Learn about and access the SmartAPI services
            </p>
        </div>
        <div class="col s12 m6 l4 center-align padding20 topic" id="specBox" @mouseenter="animatedIcons('specIcon')">
            <a target="_blank" href="https://github.com/SmartAPI/smartAPI-Specification/blob/OpenAPI.next/versions/3.0.0.md" >
                <Image alt="icon" class="margin10" img_width="70px" img_name="spec.svg" id="specIcon"></Image>
                <br>
                <h4 style="text-decoration: underline; text-transform: uppercase;" class="hide-on-med-and-up show-on-small white-text">Specification</h4>
                <span class="clearButton hide-on-small-only">Specification</span>
          </a>
            <p class="l-blue-text" >
                SmartAPI metadata specification to start your API
            </p>
        </div>
        <div class="col s12 m6 l4 center-align padding20 topic" id="guideBox" @mouseenter="animatedIcons('guideIcon')">
            <a href="/guide" >
                <Image alt="icon" class="margin10" img_width="70px" img_name="guide.svg" id="guideIcon"></Image>
                <br>
                <h4 style="text-decoration: underline; text-transform: uppercase;" class="hide-on-med-and-up show-on-small white-text">Guide</h4>
                <span class="clearButton hide-on-small-only">Guide</span>
          </a>
            <p class="l-blue-text" >
                Contribute to SmartAPI for the first time
            </p>
        </div>
        <div class="col s12 m6 l4 center-align padding20 topic" id="groupBox" @mouseenter="animatedIcons('groupIcon')">
            <a href="https://goo.gl/D4e0xL" target="_blank">
                <Image alt="icon" class="margin10" img_width="70px" img_name="group.svg" id="groupIcon"></Image>
                <br>
                <h4 style="text-decoration: underline; text-transform: uppercase;" class="hide-on-med-and-up show-on-small white-text">Working Group</h4>
                <span class="clearButton hide-on-small-only">Working Group</span>
            </a>
            <p class="l-blue-text" >
                Join the API Interoperability working group
            </p>
        </div>

    </div>
    <div class="section grey lighten-4" id="intro2">
        <div class="container">
            <div class="row">
              <div class="col l8 s12 m8">
                <h2 class="center header blue-grey-text text_h2 flow-text hide-on-small-only">Why do we need <span class="logoFont">SmartAPI</span>s? </h2>
                <!-- content for small screen only -->
                <div class="col s12 center-align hide-on-med-and-up show-on-small padding20">
                    <Image alt="image" img_width='70%' class="responsive-img" img_name="graph.jpg"></Image>
                </div>
                <h3 class="center hide-on-med-and-up show-on-small">Why do we need <span class="logoFont blue-grey-text">SmartAPI</span>s?</h3>
                <p class=" blue-grey-text">
                    Data analysis is increasingly being performed using cloud-based, web-friendly application programming interfaces (APIs). Thousands of tools and APIs are available through web service registries such as <a href="http://www.programmableweb.com/" target="_blank">Programmable Web</a>, <a href="https://www.biocatalogue.org/" target="_blank">BioCatalogue</a> and cloud platforms such as <a href="https://galaxyproject.org/" target="_blank">Galaxy</a>. Searching these and other API repositories to find a set of tools to retrieve or operate on data of interest presents a number of formidable challenges: users must not only supply the right combination of search terms, but must also closely examine the API outputs to determine whether they can be connected together. SmartAPIs tackle this challenge because they contain the rich metadata needed to precisely describe the service and the data that it operates on or provides.
                </p>
              </div>
              <div class="col s12 l4 center-align padding20 hide-on-small-only m4">
                <Image alt="image" img_width='100%' class="responsive-img introPic circle" img_name="graph.jpg"></Image>
              </div>
            </div>
        </div>
    </div>

    <div class="section" id="intro3">
        <div class="container">
          <div class="row">
            <div class="col l4 s12 center-align padding20 hide-on-small-only m4">
                <Image alt="image2" img_width='100%' class="responsive-img introPic circle" img_name="strand.jpg"></Image>
            </div>
            <div class="col l8 s12 m8">
              <h2 class="center header blue-grey-text text_h2 flow-text hide-on-small-only"> What does the <span class="logoFont">SmartAPI</span> offer? </h2>
              <!-- content for small screen only -->
              <div class="col s12 center-align hide-on-med-and-up show-on-small padding20">
                  <Image img_width='70%' class="responsive-img" img_name="strand.jpg"></Image>
              </div>
              <h3 class="center hide-on-med-and-up show-on-small">What does the <span class="logoFont blue-grey-text">SmartAPI</span> offer?</h3>
              <p class="blue-grey-text">
                Richly annotated APIs will provide the assets by which users will be able to search, browse, query, and reuse APIs. Users and intelligent agents being able to traverse a highly connected network of smartAPIs. Users will be able to automatically find APIs whose outputs are the inputs for other services. Ultimately, we envision the automatic generation of workflows that take users to where they want to go with what they have today.
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
import Vivus from 'vivus'
import $ from 'jquery'

export default {
  name: 'Home',
  components: {

  },
  data: function(){
    return{
      'particle_config': {
        "particles": {
          "number": {
            "value": 30,
          },
          "color": {
            "value": "#ffffff"
          },
          "shape": {
            "type": "circle",
            "stroke": {
              "width": 0,
              "color": "#000000"
            },
            "polygon": {
              "nb_sides": 5
            },
          },
          "opacity": {
            "value": 1,
            "random": false,
            "anim": {
              "enable": false,
              "speed": 1,
              "opacity_min": 0.1,
              "sync": false
            }
          },
          "size": {
            "value": 3,
            "random": true,
            "anim": {
              "enable": false,
              "speed": 1,
              "size_min": 0.1,
              "sync": false
            }
          },
          "line_linked": {
            "enable": true,
            "distance": 300,
            "color": "#8AC5E5",
            "opacity": 1,
            "width": 2
          },
          "move": {
            "enable": true,
            "speed": .5,
            "direction": "none",
            "random": false,
            "straight": false,
            "out_mode": "out",
            "bounce": false,
            "attract": {
              "enable": false,
              "rotateX": 600,
              "rotateY": 1200
            }
          }
        },
        "interactivity": {
          "detect_on": "canvas",
          "events": {
            "onhover": {
              "enable": false,
              "mode": "repulse"
            },
            "onclick": {
              "enable": true,
              "mode": "repulse"
            },
            "resize": true
          },
          "modes": {
            "grab": {
              "distance": 800,
              "line_linked": {
                "opacity": 1
              }
            },
            "bubble": {
              "distance": 800,
              "size": 80,
              "duration": 2,
              "opacity": 1,
              "speed": 3
            },
            "repulse": {
              "distance": 100,
              "duration": .7
            },
            "push": {
              "particles_nb": 4
            },
            "remove": {
              "particles_nb": 2
            }
          }
        },
        "retina_detect": true
      }
    }
  },
  methods: {
    particlesInit(){
      try {
        window.particlesJS("particles-js", this.particle_config);
      } catch (error) {
        console.log('%c Particles failed to load','color:coral')
      }
    },
    animatedIcons(id){
      new Vivus(id, {duration: 50});
    },
    checkCookieNotification(){
      if(!localStorage.getItem("DontShowCookies")) {
        this.$swal({
              toast: true,
              width: '90vw',
              position: 'top',
              showConfirmButton: false,
              html:'<p>This website uses cookies for analytics purposes. By continuining to use this website you are giving consent to cookies being used.<br/><a class="link" target="_blank" href="/privacy">Learn more</a> about how SmartAPI uses cookies. </p><button class="btn blue" id="cookieButton">Agree, Do Not Show Again</button> '
            });
      }
      $(document).on("click", "#cookieButton", function() {
          localStorage.setItem("DontShowCookies", "true");
          this.$swal.close();
      });
    },
  },
  mounted: function(){
    let self = this;
    self.particlesInit();
    new Vivus('whatIs', {duration: 200, type: 'oneByOne'});
    this.checkCookieNotification();
  }
}
</script>

<style lang="css" scoped>
  p.blue-grey-text{
    font-size: 1.3em;
  }
  .heroContainer{
    overflow: hidden;
  }
</style>
