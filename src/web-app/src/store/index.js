import { createStore } from 'vuex'
import {authentication} from './modules/authentication'
import {metakg} from './modules/metakg'

export default createStore({
  modules: {
    authentication,
    metakg
  }
})
