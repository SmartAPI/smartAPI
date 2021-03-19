import { createApp } from 'vue'
// Components
import App from './App.vue'
import Image from './components/Image'
import VModal from './components/VModal'
// PWA
import './registerServiceWorker'
// Companion Libs
import router from './router'
import store from './store'
// Plugins
import VueSweetalert2 from 'vue-sweetalert2';
import VueFinalModal from 'vue-final-modal'
import VueParticles from 'vue-particles'
import VueGtag from "vue-gtag-next";
// Global CSS
import 'sweetalert2/dist/sweetalert2.min.css';
import 'materialize-css/dist/css/materialize.css'
import 'material-design-icons/iconfont/material-icons.css'
import "./assets/css/app.css"
import "./assets/css/animista.css"
import "./assets/css/smartapi.css"
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
.use(VueGtag, {
    property: {
      id: "UA-139873613-1",
    //   params: {
    //     user_id: "12345",
    //     send_page_view: false,
    //     linker: {
    //       domain: ['example.com']
    //     }
    //   }
    }
  });

  // 'custom_map': {
  //   'dimension5':'registryResults',
  //   'metric1':'registry-item'
  // }

// global registration
app.component("Image", Image);
app.component("VModal", VModal);
app.mount('#app');