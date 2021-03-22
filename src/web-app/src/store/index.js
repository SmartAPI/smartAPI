import { createStore } from 'vuex'
import {authentication} from './modules/authentication'
import {metakg} from './modules/metakg'
import {faq} from './modules/faq'
import {about} from './modules/about'
import {portals} from './modules/portals'

export default createStore({
  modules: {
    authentication,
    metakg,
    faq,
    about,
    portals
  },
})
