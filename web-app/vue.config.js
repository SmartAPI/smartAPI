require = require('esm')(module);
const { routes } = require('./src/router/routes.js');

var today = new Date();
var dd = String(today.getDate()).padStart(2, '0');
var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
var yyyy = today.getFullYear();

today = yyyy + '-' + mm + '-' + dd;

module.exports = {
  pwa: {
    name: 'SmartAPI',
    themeColor: '#4A90E2',
    msTileColor: '#4A90E2'
  },
  pluginOptions: {
    // https://github.com/cheap-glitch/vue-cli-plugin-sitemap#readme
		sitemap: {
      // Only generate during production builds (default: `false`)
      productionOnly: true,
      baseURL: 'https://smart-api.info',
      outputDir: './dist',
      pretty: true,
      defaults: {
        lastmod:    today,
        changefreq: 'weekly',
        priority:   1.0,
      },
      routes,
      // If both routes and URLs are provided, they will be merged together in a single sitemap
			// urls: [
			// 	'https://example.com/',
			// 	'https://example.com/about',
			// ]
		}
	},
  configureWebpack: {
    optimization: {
      runtimeChunk: 'single',
      splitChunks: {
        chunks: 'all',
        maxInitialRequests: Infinity,
        minSize: 10000,
        maxSize: 250000,
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name(module) {
              const packageName = module.context.match(/[\\/]node_modules[\\/](.*?)([\\/]|$)/)[1];
              return `npm.${packageName.replace('@', '')}`;
            },
          },
        },
      },
    },
  },
}