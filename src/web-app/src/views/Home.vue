<template>
  <main id="index-app">
    <MetaHead
    title="SmartAPI | Home"
    ></MetaHead>
    <div class="section mainBackgroundParticle heroContainer" id="index-banner">
      <vue-particles color="#ffffff"
        :particleOpacity="1"
        linesColor="#ffffff"
        :particlesNumber="30"
        shapeType="circle"
        :particleSize="5"
        :linesWidth="2"
        :lineLinked="true"
        :lineOpacity="1"
        :linesDistance="300"
        :moveSpeed=".5"
        :hoverEffect="true"
        hoverMode="grab"
        :clickEffect="true"
        clickMode="push">
      </vue-particles>
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
    <!-- new to SmartAPI-->
    <div class="blue-grey darken-4" style="overflow: hidden; padding:50px 10px;">
      <div class="container-fluid center white-text padding20">
        <h5 class="shine">New to <span class="logoFont">SmartAPI</span>?</h5>
        <p class="lighter">
          Follow this step-by-step guide to help you contribute to SmartAPI for the first time
        </p>
        <br />
        <router-link to="/guide" class="clearButton">Start Here</router-link>
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
            <Image alt="icon" class="margin10" img_width="70px" img_name="search.svg" id="registryIcon"></Image>
            <br>
            <router-link to="/registry" class="clearButton">Registry</router-link>
            <p class="l-blue-text" >
                Search the registry of SmartAPIs
            </p>
        </div>
        <div class="col s12 m6 l4 center-align padding20 topic" id="editBox" @mouseenter="animatedIcons('editIcon')">
            <Image alt="icon" class="margin10" img_width="70px" img_name="edit.svg" id="editIcon"></Image>
            <br>
            <router-link to="/editor" class="clearButton">Editor</router-link>
            <p class="l-blue-text" >
                Author your own SmartAPI metadata
            </p>
        </div>
        <div class="col s12 m6 l4 center-align padding20 topic" id="apiBox" @mouseenter="animatedIcons('apiIcon')">
            <Image alt="icon" class="margin10" img_width="70px" img_name="api.svg" id="apiIcon"></Image>
            <br>
            <router-link to="/ui/27a5b60716c3a401f2c021a5b718c5b1" class="clearButton">API</router-link>
            <p class="l-blue-text" >
                Learn about and access the SmartAPI services
            </p>
        </div>
        <div class="col s12 m6 l4 center-align padding20 topic" id="specBox" @mouseenter="animatedIcons('specIcon')">
            <Image alt="icon" class="margin10" img_width="70px" img_name="spec.svg" id="specIcon"></Image>
            <br>
            <a class="clearButton" target="_blank" href="https://github.com/SmartAPI/smartAPI-Specification/blob/OpenAPI.next/versions/3.0.0.md" >Specification</a>
            <p class="l-blue-text" >
                SmartAPI metadata specification to start your API
            </p>
        </div>
        <div class="col s12 m6 l4 center-align padding20 topic" id="guideBox" @mouseenter="animatedIcons('guideIcon')">
            <Image alt="icon" class="margin10" img_width="70px" img_name="guide.svg" id="guideIcon"></Image>
            <br>
            <router-link to="/guide" class="clearButton">Guide</router-link>
            <p class="l-blue-text" >
                Contribute to SmartAPI for the first time
            </p>
        </div>
        <div class="col s12 m6 l4 center-align padding20 topic" id="groupBox" @mouseenter="animatedIcons('groupIcon')">
            <Image alt="icon" class="margin10" img_width="70px" img_name="group.svg" id="groupIcon"></Image>
            <br>
            <a href="https://goo.gl/D4e0xL" target="_blank" class="clearButton">Working Group</a>
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

export default {
  name: 'Home',

  methods: {
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

        document.getElementById('cookieButton').addEventListener("click", function(){
            localStorage.setItem("DontShowCookies", "true");
            this.$swal.close();
        });
      }
      
    },
  },
  mounted: function(){
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
