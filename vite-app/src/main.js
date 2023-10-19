// Components
import App from '@/App.vue'
import VModal from '@/components/VModal.vue'
import MetaHead from '@/components/MetaHead.vue'
import CopyButton from '@/components/CopyButton.vue'
// Companion Libraries
import router from '@/router'
import store from '@/store'
// Plugins
import VueSweetalert2 from 'vue-sweetalert2'
import VueFinalModal from 'vue-final-modal'
import Particles from 'vue3-particles'
import VueGtag from 'vue-gtag-next'
import Toaster from '@meforma/vue-toaster'
import { delegate } from 'tippy.js'
// Global CSS
import 'sweetalert2/dist/sweetalert2.min.css'
import 'materialize-css/dist/css/materialize.css'
import 'material-design-icons/iconfont/material-icons.css'
import '@/assets/app.css'
import '@/assets/animista.css'
import 'tippy.js/themes/light.css'

import { createApp } from 'vue'

const app = createApp(App)

app
  .use(store)
  .use(router)
  .use(VueSweetalert2)
  .use(VueFinalModal())
  .use(Particles)
  .use(Toaster)
  .use(VueGtag, {
    property: {
      id: 'UA-139873613-1'
    }
  })
// dev base api url
app.config.globalProperties.$apiUrl =
  process.env.NODE_ENV == 'development' ? 'https://dev.smart-api.info/api' : '/api'

// global registration
app.component('VModal', VModal)
app.component('MetaHead', MetaHead)
app.component('CopyButton', CopyButton)
app.mount('#app')

delegate('#app', {
  target: '[data-tippy-content]',
  theme: 'light',
  trigger: 'mouseenter',
  interactive: true,
  allowHTML: true,
  onShow(instance) {
    instance.setContent(`<div class="p-1">
      <small>${instance.reference.dataset.tippyContent}</small>
      </div>`)
  }
})
