// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import { createApp } from 'vue'
import App from './App'
import router from './router'
import helpers from '@/utils/helpers'
import api_endpoints from './api'
// vue-resource is not officially supported in Vue 3
// We need to use an alternative like axios or implement a custom plugin
// This example implements axios as a replacement
import axios from 'axios'

// Import jQuery 
import $ from 'jquery'
window.$ = window.jQuery = $  // Import jQuery and make it globally available
import 'jquery-validation'
import select2 from 'select2'  // Select2 is a jQuery-based replacement for select boxes.

// Datatable is jQuery plugin.  import here to make it globally available
import 'datatables.net-bs5'
import 'datatables.net-buttons-bs5'
import 'datatables.net-responsive-bs'
import 'datatables.net-buttons/js/dataTables.buttons.js';
import 'datatables.net-buttons/js/buttons.html5.js';

// Style imports
import 'sweetalert2/dist/sweetalert2.css';
import 'select2/dist/css/select2.min.css';
import 'select2-bootstrap-5-theme/dist/select2-bootstrap-5-theme.min.css';
import 'datatables.net-bs5/css/dataTables.bootstrap5.min.css'
import 'datatables.net-buttons-bs5/css/buttons.bootstrap5.min.css'
import 'datatables.net-responsive-bs/css/responsive.bootstrap.min.css'
import '@fortawesome/fontawesome-free/css/all.min.css'

// Vue 3 uses createApp to instantiate the application
const app = createApp(App)

// Global configuration
app.config.devtools = true
app.config.productionTip = false

// Make axios available globally as a replacement for vue-resource, but ideally using axios in each file is the recommended approach
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
