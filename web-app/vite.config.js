import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import Sitemap from 'vite-plugin-sitemap'
import axios from 'axios'

// Static routes
const staticRoutes = [
  '/',
  '/about',
  '/faq',
  '/privacy',
  '/branding',
  '/guide',
  '/dashboard',
  '/extensions/smartapi',
  '/extensions/x-bte',
  '/extensions/x-translator?',
  '/registry',
  '/registry/translator',
  '/documentation/getting-started',
  '/documentation/smartapi-extensions',
  '/documentation/openapi-specification',
  '/ui',  // For routes like /ui/:smartapi_id
  '/editor',
]

// Fetch dynamic slugs asynchronously
async function fetchDynamicRoutes() {
  try {
    const response = await axios.get('https://smart-api.info/api/query?&q=__all__&fields=_id&size=1000&raw=1')
    const dynamicRoutes = response.data.hits.map(item => `/ui/${item._id}`)  // Only return URLs as strings
    console.log('Fetched dynamic routes:', dynamicRoutes)  // Log the dynamic routes
    return dynamicRoutes
  } catch (error) {
    console.error('Error fetching dynamic routes:', error)
    return []  // Return an empty array in case of error
  }
}

// Fetch dynamic routes before config execution
const routes = await fetchDynamicRoutes()

// Combine static and dynamic routes
const dynamicRoutes = [...staticRoutes, ...routes]

export default defineConfig({
  plugins: [
    vue(),
    Sitemap({
      hostname: 'https://www.smart-api.info',
      readable: true,
      changefreq: 'monthly',
      dynamicRoutes  // Provide the combined routes as an array of strings
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
