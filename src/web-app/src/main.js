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
// Global CSS
import 'sweetalert2/dist/sweetalert2.min.css';
import 'materialize-css/dist/css/materialize.css'
import 'material-design-icons/iconfont/material-icons.css'
import "./assets/css/app.css"
import "./assets/css/animista.css"
import "./assets/css/smartapi.css"

//Create App
const app = createApp(App);

// vue dev tools on inspector
// app.config.devtools = true

app.use(store).use(router).use(VueSweetalert2).use(VueFinalModal());

// global registration
app.component("Image", Image);
app.component("VModal", VModal);
app.mount('#app');