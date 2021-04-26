const axios = require('axios');

function getSmartAPI_IDs(){
    axios.create({
        baseURL: 'https://smart-api.info', 
        proxy: false  
    })
    return axios.get('https://smart-api.info/api/query?&q=__all__&fields=_id&size=1000').then(res=>{
        return res.data.hits.map(item => item._id)
    }).catch(err=>{
        console.log(err)
        return ['']
    })
}

export const routes = [
    {
        path: '/',
        name: 'Home',
        component: () => import(/* webpackChunkName: "about" */ '../views/Home.vue')
    },
    {
        path: '/about',
        name: 'About',
        // route level code-splitting
        // this generates a separate chunk (about.[hash].js) for this route
        // which is lazy-loaded when the route is visited.
        component: () => import(/* webpackChunkName: "about" */ '../views/About.vue'),
        meta: {
            sitemap: {
                priority:    0.8,
            }
        }
    },
    {
        path: '/faq',
        name: 'FAQ',
        component: () => import('../views/FAQ.vue'),
        meta: {
            sitemap: {
                priority:    0.8,
            }
        }
    },
    {
        path: '/privacy',
        name: 'Privacy',
        component: () => import('../views/Privacy.vue'),
        meta: {
            sitemap: {
                priority:    0.8,
            }
        }
    },
    {
        path: '/add-api',
        name: 'RegisterAPI',
        component: () => import('../views/RegisterAPI.vue'),
        meta: {
            sitemap: {
                priority:    0.8,
            }
        }
    },
    {
        path: '/portal',
        name:'EmptyRouterView',
        component: () => import('../views/EmptyRouterView.vue'),
        children: [
            {
            path: '',
            name:'PortalHome',
            component: () => import('../views/PortalHome.vue')
            },
            {
            path: 'translator',
            name:'EmptyRouterView',
            component: () => import('../views/EmptyRouterView.vue'),
            children: [
                {
                path: '',
                name:'TranslatorHome',
                component: () => import('../views/TranslatorHome.vue'),
                },
                {
                path: 'summary',
                name:'Summary',
                component: () => import('../views/Summary.vue'),
                },
                {
                path: 'metakg/:component?',
                name:'MetaKG',
                component: () => import('../views/MetaKG.vue'),
                props: true,
                meta: {
                        sitemap: {
                            slugs: [
                                '',
                                'KP',
                                'ARA',
                            ],
                        }
                    }
                },
            ]
            },
        ]
    },
    {
        path: '/branding',
        name: 'Branding',
        component: () => import('../views/Branding.vue'),
        meta: {
            sitemap: {
                priority:    0.8,
            }
        }
    },
    {
        path: '/documentation/:doc?',
        name: 'Documentation',
        component: () => import('../views/Documentation.vue'),
        props: true,
        meta: {
            sitemap: {
                slugs: [
                    'getting-started',
                    'smartapi-extensions',
                    'openapi-specification'
                ],
                priority:    0.8,
            }
        }
    },
    {
        path: '/guide',
        name: 'Guide',
        component: () => import('../views/Guide.vue'),
        meta: {
            sitemap: {
                priority:    0.8,
            }
        }
    },
    {
        path: '/dashboard',
        name: 'DashBoard',
        component: () => import('../views/DashBoard.vue'),
        meta: {
            sitemap: {
                priority:    0.8,
            }
        }
    },
    {
        path: '/registry/:portal_name?',
        name: 'Registry',
        component: () => import('../views/Registry.vue'),
        meta: {
            sitemap: {
                slugs: [
                    '',
                    'translator',
                    'nihdatacommons',
                ],
            }
        }
    },
    {
        path: '/ui/:smartapi_id?',
        name: 'UI',
        component: () => import('../views/UI.vue'),
        meta: {
                sitemap: {
                    // Slugs can also be provided asynchronously
                    // The callback must always return an array
                    slugs: async () => await getSmartAPI_IDs(),
                }
            }
    },
    {
        path: '/editor/:smartapi_id?',
        name: 'Editor',
        component: () => import('../views/Editor.vue'),
        meta: {
                sitemap: {
                    // Slugs can also be provided asynchronously
                    // The callback must always return an array
                    slugs: [''],
                }
            }
    },
    {
        path: "/:catchAll(.*)",
        name: '404',
        component: () => import('../views/404.vue'),
        meta: { sitemap: { ignoreRoute: true } }
    }
]