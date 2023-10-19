<template>
  <main id="docapp" class="blue-grey darken-3 testBack">
    <MetaHead title="SmartAPI | Guide"></MetaHead>
    <!-- PROGRESS BAR -->
    <div v-if="selection" class="progress padding20" style="background-color: var(--blue-medium)">
      <div class="determinate light-blue lighten-4" :style="{ width: progressText }">
        {{ progressText || '0%' }}
      </div>
    </div>
    <!-- PROGRESS BAR -->

    <!-- start of INTRO -->
    <div v-if="!selection" class="center-align padding20">
      <div class="transparent padding20">
        <a class="hideOnSmall" target="_blank" href="https://www.openapis.org/">
          <img
            width="20%"
            alt="SmartAPI"
            src="@/assets/img/logo-small.svg"
            class="hide-on-med-only hide-on-large-only"
          />
          <img
            width="20%"
            alt="SmartAPI"
            src="@/assets/img/logo-medium.svg"
            class="hide-on-small-only hide-on-large-only"
          />
          <img
            style="max-width: 500px"
            width="30%"
            alt="SmartAPI"
            src="@/assets/img/logo-large.svg"
            class="hide-on-small-only hide-on-med-only"
          />
        </a>

        <h5 class="white-text flow-text textShadow" style="font-size: 5vw">
          <b class="logoFont">SmartAPI</b> &amp; <b>OpenAPI</b>
        </h5>
        <p class="margin20 padding20 white-text">
          SmartAPI uses OpenAPI-based specification for defining the key API metadata elements and
          value sets.<br />
          SmartAPIs leverages the Open API specification V3 and JSON-LD to provide semantically
          annotated JSON content that can be treated as Linked Data.
        </p>
        <a class="btn blue" @click="learnMore = !learnMore">Learn More</a>
      </div>
      <div
        v-show="learnMore"
        class="d-flex justify-content-center"
        style="display: none; margin-top: 15px"
      >
        <div class="p-1 white">
          <img width="100" src="@/assets/img/openapi-logo.png" class="circle" />
          <h4 class="flow-text">What is OpenAPI?</h4>
          <p class="blue-grey-text left-align">
            The
            <a class="amber-text" target="_blank" href="https://www.openapis.org/"
              >OpenAPI Initiative</a
            >
            (OAI) was created by a consortium of forward-looking industry experts who recognize the
            immense value of standardizing how REST APIs are described. As an open governance
            structure under the Linux Foundation, the OAI is focused on creating, evolving and
            promoting a vendor-neutral description format. SmartBear Software is donating the
            Swagger Specification directly to the OAI as the basis of this Open Specification.
          </p>
          <p class="blue-grey-text left-align">
            APIs form the connecting glue between modern applications. Nearly every application uses
            APIs to connect with corporate data sources, third-party data services or other
            applications. Creating an open description format for API services that is
            vendor-neutral, portable and open is critical to accelerating the vision of a truly
            connected world.
          </p>
          <hr />
          <a class="btn blue" target="_blank" href="https://www.openapis.org/">OpenAPI Website</a>
        </div>
        <div class="p-1 light-blue lighten-5">
          <img width="100" src="@/assets/img/logo-medium.svg" class="circle" />
          <h4 class="flow-text">What is SmartAPI?</h4>
          <p class="blue-grey-text left-align">
            The smartAPI project aims to maximize the FAIRness (Findability, Accessibility,
            Interoperability and Reusability) of web-based Application Programming Interfaces
            (APIs). Rich metadata is essential to properly describe your API so that it becomes
            discoverable, connected, and reusable.
          </p>
          <hr />
          <a
            class="btn blue"
            target="_blank"
            href="https://github.com/SmartAPI/smartAPI-Specification"
            >SmartAPI Specification</a
          >
        </div>
        <div class="p-1 white">
          <img width="100" src="@/assets/img/swagger-logo.jpeg" class="circle" />
          <h4 class="flow-text">
            What is the relationship between Swagger Specification and OpenAPI Spec (OAS)?
          </h4>
          <p class="blue-grey-text left-align">
            SmartBear donated the Swagger Specification in 2015 as part of the formation of the
            OpenAPI Initiative. Following the announcement of the OAI, the Swagger specification was
            renamed the OpenAPI Specification and is semantically identical to the specification
            formerly known as the Swagger 2.0 specification.
          </p>
          <p class="blue-grey-text left-align">
            OAS – and the Swagger Specification before it – is widely recognized as the most popular
            open source framework for defining and creating RESTful APIs, and today tens of
            thousands of developers are building thousands of open source repos of tools leveraging
            the OpenAPI Specification.
          </p>
        </div>
      </div>
      <div class="card-panel blue">
        <h5 class="white-text lighter bold">GUIDE</h5>
        <h4 class="white-text lighter">ADD YOUR API</h4>
        <br />
        <button type="button" class="clearButton" @click="select('start')">START</button>
      </div>
      <div class="card-panel grey lighten-4">
        <h4 class="blue-text lighter">Resources</h4>
        <hr />
        <h3 class="blue-text flow-text">
          <i class="material-icons blue-text">extension</i> SmartAPI Extensions
        </h3>

        <div class="card-panel white">
          <p>
            Most of the SmartAPI extensions are optional, but a few are REQUIRED, for example:
            <br />
            <code>info.termOfService</code><br />
            <code>info.contact.x-role</code><br />
            <code>info.version</code><br />
            For a full list of REQUIRED extensions refer to the recommendations column of the
            document here:
          </p>
          <button
            id="extBtn"
            class="btn green hideOnSmall"
            @click="
              url =
                'https://raw.githubusercontent.com/SmartAPI/smartAPI-Specification/OpenAPI.next/versions/smartapi-list.md'
              showModal = true
            "
          >
            {{ btnTxtExt }}
          </button>
          <a
            class="btn blue"
            href="https://github.com/SmartAPI/smartAPI-Specification/blob/OpenAPI.next/versions/smartapi-list.md#fixed-fields-1"
            target="_blank"
          >
            Open on Github
          </a>
          <hr />
          <VModal v-model="showModal" @confirm="confirm">
            <template v-slot:title>SmartAPI Extensions</template>
            <MarkDown :url="url"></MarkDown>
          </VModal>
        </div>
      </div>
    </div>
    <!-- Start of Guide -->

    <div v-if="selection === 'start'" class="center-align container padding20 row">
      <div class="card-panel white z-depth-5">
        <img width="200" src="@/assets/img/api-thinking.svg" alt="thinking" />
        <br />
        <h3 class="text_h3 blue-text tracking-in-expand flow-text">
          Do You Have <b>OpenAPI</b> Metadata?
        </h3>
        <button
          type="button"
          class="btn-large blue"
          @click="
            select('yes')
            setProgress(10)
          "
        >
          YES
        </button>
        <button
          type="button"
          class="btn-large red"
          @click="
            select('no')
            setProgress(50)
          "
        >
          NO
        </button>
      </div>

      <div class="card-panel grey lighten-4">
        <h3 class="text_h3 blue-text flow-text">Back to Introduction</h3>
        <hr />
        <button
          type="button"
          class="btn red"
          @click="
            select('start')
            setProgress(-10)
            selection = ''
          "
        >
          Go Back
        </button>
      </div>
    </div>
    <!-- if YES ask for version -->
    <div
      v-if="selection === 'yes'"
      class="center-align container padding20"
      style="position: relative"
    >
      <button
        type="button"
        @click="
          select('start')
          setProgress(-10)
        "
        style="position: absolute; top: 0; left: 0; margin: 40px; cursor: pointer"
      >
        <i class="fa fa-arrow-circle-o-left fa-2x red-text" aria-hidden="true"></i>
      </button>
      <div class="card-panel white z-depth-5">
        <img width="200" src="@/assets/img/api-thinking.svg" alt="thinking" />
        <br />
        <h3 class="text_h3 blue-text tracking-in-expand flow-text">Which Version Do You Have?</h3>
        <button
          type="button"
          class="waves-effect waves-light btn-large blue"
          @click="
            select('2')
            setProgress(40)
          "
        >
          Version 2
        </button>
        <button
          type="button"
          class="waves-effect waves-light btn-large green"
          @click="
            select('3')
            setProgress(40)
          "
        >
          Version 3
        </button>
      </div>
      <div class="card-panel grey lighten-4">
        <h3 class="text_h3 blue-text flow-text">Don't Know Which Version You Have?</h3>
        <div class="row">
          <div class="card-panel white blue-text col s12 l6 padding20">
            <h5 class="flow-text">Version 2</h5>
            <a target="_blank" href="https://swagger.io/">
              <img
                class="responsive-img circle hoverable"
                width="50%"
                src="@/assets/img/swagger-logo.jpeg"
                alt="swagger v2"
              />
            </a>
            <p>Visit the links below for examples and version specification.</p>
            <a
              class="chip hoverable blue white-text"
              target="_blank"
              href="https://github.com/OAI/OpenAPI-Specification/blob/master/examples/v2.0/yaml/petstore-simple.yaml"
              >V2 Example</a
            >
            <br />
            <a
              class="chip hoverable blue white-text"
              target="_blank"
              href="https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md"
              >V2 Specification</a
            >
          </div>
          <div class="card-panel white blue-text col s12 l6 padding20">
            <h5 class="flow-text">Version 3</h5>
            <a target="_blank" href="https://www.openapis.org/">
              <img
                class="responsive-img circle hoverable"
                width="50%"
                src="@/assets/img/openapi-logo.png"
                alt="openAPI v3"
              />
            </a>
            <p>Visit the links below for examples and version specification.</p>
            <a
              class="chip hoverable blue white-text"
              target="_blank"
              href="https://github.com/OAI/OpenAPI-Specification/blob/master/examples/v3.0/petstore.yaml"
              >V3 Example</a
            >
            <br />
            <a
              class="chip hoverable blue white-text"
              target="_blank"
              href="https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md"
              >V3 Specification</a
            >
          </div>
        </div>
      </div>
    </div>
    <!-- if NO start from scratch -->
    <!--  -->
    <div
      v-if="selection === 'no'"
      class="center-align container padding20 white"
      style="position: relative"
    >
      <button
        type="button"
        @click="
          select('start')
          setProgress(-40)
        "
        style="position: absolute; top: 0; left: 0; margin: 40px; cursor: pointer"
      >
        <i class="fa fa-arrow-circle-o-left fa-2x red-text" aria-hidden="true"></i>
      </button>
      <div class="card-panel transparent">
        <h3 class="blue-grey-text tracking-in-expand flow-text">Start From Scratch</h3>
        <ul class="collection transparent" style="border: none">
          <li class="collection-item transparent">
            <img class="margin10" width="120" src="@/assets/img/v0.svg" id="editIcon" />
            <br />
            <h3 class="blue-text flow-text">
              <i class="fa fa-check-square-o blue-text" aria-hidden="true"></i> Create and Edit Your
              V3 OpenAPI Metadata
            </h3>
            <p class="flow-text blue-grey-text">
              You can start with an existing metadata example below. The editor automatically
              validates your API metadata and gives a live preview of auto-generated API
              documentation.
            </p>
            <h5 class="flow-text blue-text">Metadata Examples</h5>
            <ul>
              <li class="blue-text">
                <a
                  class="blue-text"
                  href="https://github.com/NCATS-Tangerine/translator-api-registry/blob/master/mygene.info/openapi_minimum.yml"
                  target="_blank"
                >
                  <i class="material-icons">link</i> MyGene.info</a
                >
              </li>
              <li class="blue-text">
                <a
                  class="blue-text"
                  href="https://github.com/NCATS-Tangerine/translator-api-registry/blob/master/myvariant.info/openapi_minimum.yml"
                  target="_blank"
                >
                  <i class="material-icons">link</i> MyVariant.info</a
                >
              </li>
            </ul>
            <router-link to="/editor" class="btn-large editor green margin20">Editor</router-link>
            <p class="grey-text left-align">
              Note: This
              <a target="_blank" href="https://mermade.github.io/openapi-gui/">OpenAPI GUI</a>
              interface can also be useful for creating your API metadata from scratch. But be aware
              that this interface does not support any
              <a
                target="_blank"
                href="https://github.com/SmartAPI/smartAPI-Specification/blob/OpenAPI.next/versions/smartapi-list.md"
                >SmartAPI extensions</a
              >
              (those fields with "x-" prefix) we added to the standard OpenAPI v3 specifications.
              You can, of course, add extra SmartAPI fields after you export your metadata from the
              GUI interface to the editor. You will add those extensions at a later step.
            </p>
            <p class="grey-text">For a complete list of SmartAPI extensions, visit this link:</p>
            <a
              class="btn blue"
              href="https://github.com/SmartAPI/smartAPI-Specification/blob/OpenAPI.next/versions/smartapi-list.md#fixed-fields-1"
              target="_blank"
              >Extensions</a
            >
          </li>
          <li class="collection-item nextBox padding20">
            <h4 class="white-text flow-text">Done Creating Your V3 Metadata?</h4>
            <br />
            <a
              class="clearButton"
              @click.prevent="
                select('3')
                setProgress(30)
              "
              >NEXT</a
            >
          </li>
        </ul>
      </div>
    </div>
    <!-- if VERSION 2 -->
    <div
      v-if="selection === '2'"
      class="center-align container padding20 white"
      style="position: relative"
    >
      <a
        @click.prevent="
          select('yes')
          setProgress(-40)
        "
        style="position: absolute; top: 0; left: 0; margin: 40px; cursor: pointer"
        ><i class="fa fa-arrow-circle-o-left fa-2x red-text" aria-hidden="true"></i
      ></a>
      <div class="card-panel transparent">
        <h3 class="blue-grey-text tracking-in-expand flow-text">Version 2</h3>
        <img class="margin10" width="120" src="@/assets/img/v2.svg" id="editIcon" />

        <p class="blue-grey-text flow-text">
          If you already have an API metadata document in older
          <b>Swagger/OpenAPI V2</b> specification you will need to follow these steps to convert
          your metadata to the latest <b>OpenAPI V3</b> format, and then edit it in the editor
          below.
        </p>
        <div class="card yellow lighten-4">
          <div class="card-content blue-grey-text">
            <span class="card-title">Submit Swagger V2 Metadata</span>
            <p>
              <i class="material-icons red-text">warning</i> You may submit your V2 metadata as it
              is up to this point, however you will experience <b>limited functionality</b>.
            </p>
            <a
              class="link"
              target="_blank"
              href="https://github.com/SmartAPI/smartAPI-Specification/blob/OpenAPI.next/versions/3.0.0.md"
              >Learn More about OpenAPI V3 Specification</a
            >
            <hr />
            <p class="bold">
              We recommend you continue with this process to convert your metadata to OpenAPI v3
              metadata to be fully compatible with SmartAPI and BiotThings Explorer.
            </p>
          </div>
          <div class="card-action">
            <router-link to="/add-api" class="btn green">Add Your V2 API Anyway</router-link>
          </div>
        </div>
        <ul class="collection noBorder">
          <li class="collection-item">
            <i class="material-icons medium blue-text">code</i>
            <br />
            <h3 class="blue-text flow-text">
              <i class="fa fa-check-square-o blue-text" aria-hidden="true"></i> CONVERT YOUR
              METADATA:
            </h3>
            <p class="blue-grey-text flow-text">
              Use any of these two options to convert your V2 Metadata to V3 Metadata.
            </p>
            <div class="row">
              <div class="col s12 l6 white blue-text center-align padding20">
                <p class="blue-text flow-text">Tavis OpenAPI Converter</p>
                <a
                  title="Tavis OpenAPI V3 Converter"
                  class="btn-large green"
                  target="_blank"
                  href="http://openapiconverter.azurewebsites.net/"
                  >Converter 1</a
                >
                <br />
              </div>
              <div class="col s12 l6 white blue-text center-align padding20">
                <p class="blue-text flow-text">Mermade Converter</p>
                <a
                  title="Mermade Converter"
                  class="btn-large green"
                  target="_blank"
                  href="https://mermade.org.uk/openapi-converter"
                  >Converter 2</a
                >
                <br />
              </div>
              <div class="col s12 l12 white blue-text center-align padding20">
                <hr />
                <p class="grey-text flow-text">Other Conversion Tools:</p>
                <h5 class="blue-text flow-text">Api-Spec-Converter</h5>
                <a
                  title="api-spec-converter"
                  class="center-align"
                  target="_blank"
                  href="https://www.npmjs.com/package/api-spec-converter"
                >
                  <img width="50" src="@/assets/img/npmlogo.png" alt="npm package" />
                </a>
                <br />
              </div>
            </div>
            <p class="grey-text">
              <b>Tip:</b> Feel free to play with your API metadata file with the tools we mentioned
              above, and commit your changes even when they are not fully complete or valid.
            </p>
          </li>
          <li class="collection-item nextBox padding20">
            <h4 class="white-text flow-text">Done Converting Your Metadata?</h4>
            <br />
            <button
              type="button"
              class="clearButton"
              @click="
                select('3')
                setProgress(30)
              "
            >
              NEXT
            </button>
          </li>
        </ul>
      </div>
    </div>
    <!-- if VERSION 3 -->
    <div
      v-if="selection === '3'"
      class="center-align container padding20 white"
      style="position: relative"
    >
      <button
        type="button"
        @click="
          select('yes')
          setProgress(-40)
          completeToDo(1)
          completeToDo(2)
          completeToDo(3)
        "
        style="position: absolute; top: 0; left: 0; margin: 40px; cursor: pointer"
      >
        <i class="fa fa-arrow-circle-o-left fa-2x red-text" aria-hidden="true"></i>
      </button>

      <div class="card-panel transparent">
        <h3 class="blue-text tracking-in-expand flow-text">Version 3</h3>
        <img class="margin10" width="120" src="@/assets/img/v3.svg" id="editIcon" />
        <table class="bordered">
          <tbody>
            <!-- STEP 1 -->
            <tr>
              <td class="center-align">
                <h3 class="blue-text flow-text">
                  <i class="fa fa-check-square-o blue-text" aria-hidden="true"></i> Validate Your
                  Metadata
                </h3>
                <p class="blue-grey-text flow-text">
                  Validate your metadata and clear all errors using this editor:
                </p>
                <router-link to="/editor" class="btn green">Editor</router-link>
                <br />
                <i class="fa fa-arrow-down light-blue-text fa-2x margin20" aria-hidden="true"></i>
              </td>
            </tr>

            <!-- STEP 2 -->
            <tr>
              <td class="center-align">
                <h3 class="blue-text flow-text">
                  <i class="fa fa-check-square-o blue-text" aria-hidden="true"></i> Host Your
                  Metadata
                </h3>
                <p class="blue-grey-text flow-text">
                  Host your metadata in a version-control system. On your own Github repository or
                  on <a href="#hosting">our project specific repositories</a>.
                </p>
                <a class="btn green white-text" href="#hosting">Hosting Info</a>
                <br />
                <i class="fa fa-arrow-down light-blue-text fa-2x margin20" aria-hidden="true"></i>
              </td>
            </tr>

            <tr>
              <td class="center-align">
                <h3 class="blue-text flow-text">
                  <i class="fa fa-check-square-o blue-text" aria-hidden="true"></i> Add Required
                  SmartAPI Extensions
                </h3>
                <p class="blue-grey-text flow-text">
                  Most of the SmartAPI extensions are optional, but a few are <b>required</b>, for
                  example:
                </p>
                <ul class="padding20 grey lighten-5">
                  <li><code>info.termOfService</code></li>
                  <li><code>info.contact.x-role</code></li>
                  <li><code>info.version</code></li>
                </ul>

                <p class="blue-grey-text flow-text">
                  For a full list of required extensions refer to the recommendations column of the
                  document here:
                </p>
                <a
                  class="btn green"
                  target="_blank"
                  href="https://github.com/SmartAPI/smartAPI-Specification/blob/OpenAPI.next/versions/smartapi-list.md#fixed-fields-1"
                  >Extensions</a
                >
                <br />
                <i class="fa fa-arrow-down light-blue-text fa-2x margin20" aria-hidden="true"></i>
              </td>
            </tr>
            <tr class="nextBox padding20" v-if="!todo1 && !todo2 && !todo3">
              <td class="center-align">
                <h4 class="white-text flow-text">Completed All Steps?</h4>
                <br />
                <a
                  class="clearButton"
                  @click="
                    completeToDo(1)
                    completeToDo(2)
                    completeToDo(3)
                    setProgress(50)
                  "
                  >NEXT</a
                >
              </td>
            </tr>
          </tbody>
        </table>
        <div
          id="submitBox"
          v-if="todo1 && todo2 && todo3"
          class="card-panel green padding20"
          style="border-radius: 20px"
        >
          <h3 class="white-text flow-text textShadow">You're Ready To Submit Your Metadata!</h3>
          <router-link to="/add-api" class="clearButton margin20">Add Your API</router-link>
          <div class="card-panel grey lighten-4 margin20">
            <p class="blue-grey-text">
              <b>Important!</b> Before submitting make sure to copy the URL to the RAW content!
            </p>
            <img src="@/assets/img/raw.gif" width="300" alt="raw content" class="responsive-img" />
          </div>
        </div>
      </div>
      <!-- Hosting Information -->
      <div class="card-panel blue-grey darken-4 white-text">
        <h2 class="white-text flow-text">Hosting</h2>
      </div>
      <div id="hosting" class="card-panel grey lighten-4">
        <h3 class="blue-text flow-text">
          <i class="fa fa-github-square blue-text"></i> Host Your Metadata With Us
        </h3>
        <div class="card-panel white">
          <p class="blue-grey-text flow-text">
            The link below provides an optional place for those who need to have a place to host
            their own API metadata.
          </p>

          <ul class="collection left-align">
            <li class="collection-item blue-grey-text">
              <div class="chip red white-text smallFont">1</div>
              Each API should create a separate folder to host its metadata. The folder
              "_example_api" provides a basic template for adding API metadata, so you can start
              with copying the "_example_api" folder and renaming it to your API name.
            </li>
            <li class="collection-item blue-grey-text">
              <div class="chip red white-text smallFont">2</div>
              Fill in the metadata about your API according to the instructions. Also, please refer
              to the existing examples like
              <a
                href="https://github.com/NCATS-Tangerine/translator-api-registry/blob/master/mygene.info/openapi_minimum.yml"
                target="_blank"
                >mygene.info</a
              >
              and
              <a
                href="https://github.com/NCATS-Tangerine/translator-api-registry/blob/master/myvariant.info/openapi_minimum.yml"
                target="_blank"
                >myvariant.info</a
              >
              APIs.
            </li>
            <li class="collection-item blue-grey-text">
              <div class="chip red white-text smallFont">3</div>
              Add an entry to the
              <a
                target="_blank"
                href="https://github.com/NCATS-Tangerine/translator-api-registry/blob/master/API_LIST.yml"
                >API_LIST.yml</a
              >
              file following the existing example. This is the master list of the APIs available in
              this repo. Our SmartAPI application will import all the API metadata based on this
              file.
            </li>
            <li class="collection-item center-align smallFont">
              <p class="blue-grey-text flow-text">
                Choose the appropiate project to host your metadata under:
              </p>
              <div class="row">
                <div class="s12 m6 l6 col">
                  <a
                    class="btn-large green"
                    target="_blank"
                    href="https://github.com/NCATS-Tangerine/translator-api-registry"
                    >NCATS Translator Project</a
                  >
                  <br />
                  <br />
                  <a
                    class="chip blue white-text"
                    target="_blank"
                    href="https://ncats.nih.gov/translator"
                    >NCATS More Info</a
                  >
                </div>
                <div class="s12 m6 l6 col">
                  <a
                    class="btn-large green"
                    target="_blank"
                    href="https://github.com/SmartAPI/smartapi_registry"
                    >SmartAPI Project</a
                  >
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>
      <div class="card-panel blue-grey darken-4 white-text">
        <h2 class="white-text flow-text">Advanced</h2>
      </div>
      <div class="card-panel grey lighten-4">
        <i class="material-icons blue-text large">developer_board</i>
        <h3 class="blue-text flow-text"><b>CORS</b> Support</h3>
        <p class="blue-grey-text flow-text">
          If you want users to be able to request your API from the browser, e.g. in a web
          application, your API should support
          <a target="_blank" href="https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS">CORS</a>.
          We recommend every public API to support CORS. Depending on your web server (e.g. Apache
          or Nginx) and/or the web framework (e.g. Django, Flask, Tornado) you use, you can find the
          relevant instruction to enable CORS for your API
          <a target="_blank" href="https://enable-cors.org/">here</a>, or via Google.
        </p>
      </div>
      <div class="card-panel grey lighten-4">
        <i class="material-icons blue-text large">settings_ethernet</i>
        <h3 class="blue-text flow-text">How to choose URIs for annotating API input/output</h3>
        <p class="blue-grey-text flow-text">
          Typically for a JSON-based REST API, we use
          <a target="_blank" href="https://en.wikipedia.org/wiki/Uniform_Resource_Identifier"
            >URIs</a
          >
          to annotate both the acceptable parameter value types and the fields from the response
          data object, both in SmartAPI metdata files and/or JSON-LD context files.
        </p>
        <p class="blue-grey-text flow-text">
          To help you decide which URIs to use, we maintain an
          <a
            target="_blank"
            href="https://github.com/NCATS-Tangerine/translator-api-registry/blob/master/ID_MAPPING.csv"
            >ID_MAPPING.csv</a
          >
          file to keep records of all URIs we will use. Feel free to add URIs for additional field
          types. Please make sure not to break the CSV format, as that will break GitHub's nice CSV
          rendering and search features.
        </p>
      </div>
    </div>
  </main>
</template>

<script>
import MarkDown from '../components/MarkDown.vue'

export default {
  name: 'Guide',
  data: function () {
    return {
      selection: '',
      todo1: false,
      todo2: false,
      todo3: false,
      btnTxtExt: 'SHOW EXTENSIONS',
      progress: 0,
      progressText: '',
      url: '',
      showModal: false,
      learnMore: false
    }
  },
  components: {
    MarkDown
  },
  methods: {
    confirm() {
      this.showModal = false
    },
    select: function (input) {
      // possible selections:
      // start - starts guide
      // intro - back to intro
      // yes - have metadata then ask for version
      // no - start from scratch
      // 2 - version 2 steps to convert metadata
      // 3 - steps to sumbit metadata
      this.selection = input
      // scroll to top after selection
      scroll(0, 0)
    },
    setProgress(input) {
      if (input == 'reset' || this.progress < 0) {
        this.progress = 0
        this.progressText = this.progress.toString() + '%'
      } else {
        if (this.progress + input < 100) {
          this.progress += input
          this.progressText = this.progress.toString() + '%'
        } else if (this.progress + input > 100) {
          this.progress = 100
          this.progressText = this.progress.toString() + '%'
        }
      }
    },
    completeToDo: function (todo) {
      // upon completing and checking all 3 checklists items
      // the upload template will show up
      switch (todo) {
        case 1:
          this.todo1 = !this.todo1
          break
        case 2:
          this.todo2 = !this.todo2
          break
        case 3:
          this.todo3 = !this.todo3
          break
        default:
          return false
      }
    }
  }
}
</script>

<style></style>
