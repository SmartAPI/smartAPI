import { createApp } from 'vue'
// Components
import App from './App.vue'
import Image from './components/Image'
import VModal from './components/VModal'
import MetaHead from './components/MetaHead'
import CopyButton from './components/CopyButton'
// PWA disabled for now
// import './registerServiceWorker'

// Companion Libs
import router from './router'
import store from './store'
// Plugins
import VueSweetalert2 from 'vue-sweetalert2';
import VueFinalModal from 'vue-final-modal'
import VueParticles from 'vue-particles'
import VueGtag from "vue-gtag-next";
import Toaster from '@meforma/vue-toaster';
import { delegate } from "tippy.js";
// import { createMetaManager } from 'vue-meta'
// Global CSS
import 'sweetalert2/dist/sweetalert2.min.css';
import 'materialize-css/dist/css/materialize.css'
import 'material-design-icons/iconfont/material-icons.css'
import "./assets/css/app.css"
import "./assets/css/animista.css"
import 'tippy.js/themes/light.css'


//Create App
const app = createApp(App);

// vue dev tools on inspector
// app.config.devtools = true

app.use(store)
.use(router)
.use(VueSweetalert2)
.use(VueFinalModal())
.use(VueParticles)
.use(Toaster)
// .use(createMetaManager())
.use(VueGtag, {
  property: {
    id: "UA-139873613-1"
  }
});
// dev base api url
app.config.globalProperties.$apiUrl = process.env.NODE_ENV == 'development' ? 'https://dev.smart-api.info/api' : '/api';
// global registration
app.component("Image", Image);
app.component("VModal", VModal);
app.component("MetaHead", MetaHead);
app.component("CopyButton", CopyButton);
app.mount('#app');

delegate("#app", {
    target: "[data-tippy-content]",
    theme: "light",
    trigger: "mouseenter",
    interactive: true,
    allowHTML: true,
    onShow(instance){
      instance.setContent(`<div class="p-1">
      <small>${instance.reference.dataset.tippyContent}</small>
      </div>`);
    }
  });