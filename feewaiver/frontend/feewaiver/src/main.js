// // The Vue build version to load with the `import` command
// // (runtime-only or standalone) has been set in webpack.base.conf with an alias.
// import Vue from 'vue'
// import resource from 'vue-resource'
// import App from './App'
// import router from './router'
// import helpers from '@/utils/helpers'
// import api_endpoints from './api'
// require( '../node_modules/bootstrap/dist/css/bootstrap.css' );
// //require('../node_modules/eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.min.css')
// require( '../node_modules/font-awesome/css/font-awesome.min.css' )

// Vue.config.devtools = true;
// Vue.config.productionTip = false
// Vue.use( resource );

// // Add CSRF Token to every request
// Vue.http.interceptors.push( function ( request, next ) {
//   // modify headers
//   if ( request.url != api_endpoints.countries ) {
//     request.headers.set( 'X-CSRFToken', helpers.getCookie( 'csrftoken' ) );
//   }

//   // continue to next interceptor
//   next();
// } );


// /* eslint-disable no-new */
// new Vue( {
//   el: '#app',
//   router,
//   template: '<App/>',
//   components: {
//     App
//   }
// } )

// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import { createApp } from 'vue'
import App from './App'
import router from './router'
import helpers from '@/utils/helpers'
import api_endpoints from './api'

// Style imports
import '../node_modules/bootstrap/dist/css/bootstrap.css'
//import '../node_modules/eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.min.css'
import '../node_modules/font-awesome/css/font-awesome.min.css'

// Vue 3 uses createApp to instantiate the application
const app = createApp(App)

// vue-resource is not officially supported in Vue 3
// We need to use an alternative like axios or implement a custom plugin
// This example implements axios as a replacement
import axios from 'axios'

// Global configuration
app.config.devtools = true
app.config.productionTip = false

// Make axios available globally as a replacement for vue-resource
app.config.globalProperties.$http = axios
// Add interceptor to include CSRF token in all requests
axios.interceptors.request.use(function(config) {
  if (config.url !== api_endpoints.countries) {
    config.headers['X-CSRFToken'] = helpers.getCookie('csrftoken')
  }
  return config
})

// Register plugins
app.use(router)

// Vue 3 uses a different mounting approach
app.mount('#app')

router.afterEach((to) => {
  console.log('Route changed to:', to.path);
  console.log('Route component:', to.matched[0]?.components?.default);
});
