import axios from 'axios'

export const authentication = {
  state: () => ({
    userInfo: {},
    loggedIn: false
  }),
  mutations: {
    saveUser(state, payload) {
      state.userInfo = payload['user']
      state.loggedIn = Object.prototype.hasOwnProperty.call(state.userInfo, 'login') ? true : false
    },
    resetUser(state) {
      state.userInfo = {}
      state.loggedIn = false
    }
  },
  actions: {
    checkUser({ commit }) {
      if (process.env.NODE_ENV == 'development') {
        // for dev only
        commit('saveUser', {
          user: {
            name: 'Marco Cano',
            email: 'artofmarco@gmail.com',
            login: 'marcodarko',
            avatar_url: 'https://avatars.githubusercontent.com/u/23092057?v=4'
          }
        })
      } else {
        axios
          .get('/user')
          .then((response) => {
            commit('saveUser', { user: response.data })
          })
          .catch((err) => {
            commit('resetUser')
            throw err
          })
      }
    }
  },
  getters: {
    userInfo: (state) => {
      return state.userInfo
    },
    loggedIn: (state) => {
      return state.loggedIn
    }
  }
}
