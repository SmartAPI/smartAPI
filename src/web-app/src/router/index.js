import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import axios from 'axios'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/about',
    name: 'About',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/About.vue')
  },
  {
    path: '/faq',
    name: 'FAQ',
    component: () => import('../views/FAQ.vue')
  },
  {
    path: '/privacy',
    name: 'Privacy',
    component: () => import('../views/Privacy.vue')
  },
  {
    path: '/add-api',
    name: 'RegisterAPI',
    component: () => import('../views/RegisterAPI.vue')
  },
  {
    path: '/editor/:smartapi_id?',
    name: 'Editor',
    component: () => import('../views/Editor.vue')
  },
  {
    path: '/ui/:smartapi_id?',
    name: 'UI',
    component: () => import('../views/UI.vue')
  },
  {
    path: '/portal',
    name:'PortalNav',
    component: () => import('../views/PortalNav.vue'),
    children:[
      {
        path: '',
        name:'PortalHome',
        component: () => import('../views/PortalHome.vue')
      },
      {
        path: ':name',
        name:'Portal',
        component: () => import('../views/Portal.vue'),
        props: true
      },
      {
        path: ':name/summary',
        name:'Summary',
        component: () => import('../views/Summary.vue'),
      },
      {
        path: ':name/metakg',
        name:'MetaKG',
        component: () => import('../views/MetaKG.vue'),
      },
    ]
  },
  {
    path: '/branding',
    name: 'Branding',
    component: () => import('../views/Branding.vue')
  },
  {
    path: '/documentation',
    name: 'Documentation',
    component: () => import('../views/Documentation.vue')
  },
  {
    path: '/guide',
    name: 'Guide',
    component: () => import('../views/Guide.vue')
  },
  {
    path: '/dashboard',
    name: 'DashBoard',
    component: () => import('../views/DashBoard.vue')
  },
  {
    path: '/registry/:portal_name?',
    name: 'Registry',
    component: () => import('../views/Registry.vue')
  },
]

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

      axios.get('http://dev.smart-api.info/api/metadata/'+slug+'?fields=_id&raw=1').then(res=>{

          if(Object.prototype.hasOwnProperty.call(res.data, "_id")){
            next({name:'UI', params: {smartapi_id : res.data._id}})
          }else next()

        }).catch(err=>{
          next()
          throw err;
        });
    }else next()

  }else next()
})

export default router
