import { createApp } from 'vue'
// Components
import App from './App.vue'
import Image from './components/Image'
import VModal from './components/VModal'
import MetaHead from './components/MetaHead'
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
.use(VueGtag, {
  property: {
    id: "UA-139873613-1"
  }
});

// global registration
app.component("Image", Image);
app.component("VModal", VModal);
app.component("MetaHead", MetaHead);
app.mount('#app');