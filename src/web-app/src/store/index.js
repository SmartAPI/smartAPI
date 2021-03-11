import { createStore } from 'vuex'
import {authentication} from './modules/authentication'
import {metakg} from './modules/metakg'
import {faq} from './modules/faq'
import {about} from './modules/about'

export default createStore({
  modules: {
    authentication,
    metakg,
    faq,
    about
  },
})
