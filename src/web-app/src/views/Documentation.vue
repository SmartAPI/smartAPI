<template>
  <main id="docs-app" style="width: 100%;">
      <MetaHead title="SmartAPI | Documentation"></MetaHead>
  <div class="row">
    <div class="testBack padding20">
    <nav>
        <div class="nav-wrapper blue">
            <ul id="nav-mobile" class="left">
            <li >
                <router-link
                to="/documentation">
                Introduction
                </router-link>
            </li>
            <li >
                <router-link
                to="/documentation/getting-started">
                Getting Started
                </router-link>
            </li>
            <li >
                <router-link
                to="/documentation/smartapi-extensions">
                SmartAPI Extensions
                </router-link>
            </li>
            <li >
                <router-link
                to="/documentation/openapi-specification">
                OpenAPI Spedcification
                </router-link>
            </li>
            </ul>
            </div>
        </nav>
        <div class="container white padding20 contentDocs z-depth-4">
            <templatem v-if='!url'>
                <h3 class="logoFont blue-text center-align flow-text">SmartAPI Documentation</h3>
                <hr />
                <div class="center-align">
                    <Image img_width="200px" img_name="logo-large.svg" alt="logo"></Image>
                    <h4 class="center-align blue-grey-text">What is a <span class="logoFont">SmartAPI</span>?</h4>
                    <p class="intro-text blue-grey-text">
                        The SmartAPI project aims to maximize the FAIRness (Findability, Accessibility, Interoperability, and Reusability) of web-based Application Programming Interfaces (APIs). Rich metadata is essential to properly describe your API so that it becomes discoverable, connected, and reusable. We have developed a <a href="http://openapis.org" target="_blank"></a>openAPI-based <a href="https://github.com/SmartAPI/smartAPI-Specification/blob/OpenAPI.next/versions/3.0.0.md" target="_blank"> specification</a> for defining the key API metadata elements and value sets. SmartAPI's leverage the <a href="https://www.openapis.org/" target="_blank">Open API specification v3 </a> and <a href="http://json-ld.org" target="_blank">JSON-LD</a> for providing semantically annotated JSON content that can be treated as <a href="http://linkeddata.org/" target="_blank">Linked Data</a>.
                    </p>
                    <hr />
                    <h4 class="blue-grey-text center-align">Why do we need <span class="logoFont">SmartAPI</span>s?</h4>
                    <p class="intro-text blue-grey-text">
                        Data analysis is increasingly being performed using cloud-based, web-friendly application programming interfaces (APIs). Thousands of tools and APIs are available through web service registries such as <a href="http://www.programmableweb.com/" target="_blank">Programmable Web</a>, <a href="https://www.biocatalogue.org/" target="_blank">BioCatalogue</a> and cloud platforms such as <a href="https://galaxyproject.org/" target="_blank">Galaxy</a>. Searching these and other API repositories to find a set of tools to retrieve or operate on data of interest presents a number of formidable challenges: users must not only supply the right combination of search terms, but must also closely examine the API outputs to determine whether they can be connected together. SmartAPIs tackle this challenge because they contain the rich metadata needed to precisely describe the service and the data that it operates on or provides.
                    </p>
                </div>
            </templatem>
            <MarkDown v-show="url" :url="url"></MarkDown>
        </div>
    </div>
  </div>
</main>
</template>

<script>
import MarkDown from '../components/MarkDown.vue'

export default {
    name: 'Documentation',
    data: function(){
        return {
            url: ''
        }
    },
    props:['doc'],
    components:{
        MarkDown
    },
    methods:{
        handleDoc(){
            switch (this.doc) {
                case 'getting-started':
                    this.url = "https://raw.githubusercontent.com/SmartAPI/smartAPI/master/README.md"
                    break;
                case 'smartapi-extensions':
                    this.url = "https://raw.githubusercontent.com/SmartAPI/smartAPI-Specification/OpenAPI.next/versions/smartapi-list.md"
                    break;
                case 'openapi-specification':
                    this.url = "https://raw.githubusercontent.com/SmartAPI/smartAPI-Specification/OpenAPI.next/README.md"
                    break;
                default:
                    this.url = ""
                    break;
            }
        }
    },
    watch:{
        doc: function(){
            this.handleDoc()
        }
    },
    mounted:function(){
        if(Object.prototype.hasOwnProperty.call(this.$route.query, 'url')){
            this.url = this.$route.query.url
        }else{
            this.handleDoc()
        }
    }
}
</script>