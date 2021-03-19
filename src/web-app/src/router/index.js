import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'

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
    path: '/portal/:name?',
    name: 'Portal',
    component: () => import('../views/Portal.vue')
  },
  {
    path: '/portal/translator/metakg',
    name: 'MetaKG',
    component: () => import('../views/MetaKG.vue')
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
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
  scrollBehavior() {
    return { x: 0, y: 0 };
  },
})

export default router
