import { createRouter, createWebHistory } from 'vue-router'
import axios from 'axios'
import {routes} from './routes.js'


const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
  linkActiveClass: "route-active",
  scrollBehavior() {
    return { x: 0, y: 0 };
  },
})

router.beforeEach((to, from, next) => {

  if (to.name === 'Home') {

    const slug = window.location.host.split('.')[0]

    if(!['www', 'dev', 'smart-api', 'localhost:8000', 'localhost:8080'].includes(slug)){

      axios.get('/api/metadata/'+slug+'?fields=_id&raw=1').then(res=>{

          if(Object.prototype.hasOwnProperty.call(res.data, "_id")){
            next({name:'UI', params: {smartapi_id : res.data._id}})
            try {
              //hack to change url back to home
              history.pushState({}, '', '/');
            } catch (e) {
              console.log(`unable to change url because ${e}`)
            }
          }else next()

        }).catch(err=>{
          next()
          throw err;
        });
    }else next()

  }else next()
})

export default router
