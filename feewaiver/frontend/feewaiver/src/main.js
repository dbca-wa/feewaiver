import 'vite/modulepreload-polyfill';
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import helpers from '@/utils/helpers'
import api_endpoints from './api'
import axios from 'axios'
import $ from 'jquery'
import _ from 'lodash'
import moment from 'moment'
import Swal from 'sweetalert2'
import select2 from 'select2'

// Make globals available on window
window.$ = window.jQuery = $
window._ = _
window.moment = moment
window.Swal = Swal

// Attach select2 to jQuery
select2($)
import 'bootstrap'
import 'jquery-validation'
// import select2 from 'select2'  // Select2 is a jQuery-based replacement for select boxes.

// Datatable is jQuery plugin.  import here to make it globally available
import 'datatables.net-bs5'
import 'datatables.net-buttons-bs5'
import 'datatables.net-responsive-bs5'
import 'datatables.net-buttons/js/dataTables.buttons.js';
import 'datatables.net-buttons/js/buttons.html5.js';

// Style imports
import 'sweetalert2/dist/sweetalert2.css';
import 'select2/dist/css/select2.css';
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import 'select2-bootstrap-5-theme/dist/select2-bootstrap-5-theme.css';
import 'datatables.net-bs5/css/dataTables.bootstrap5.min.css'
import 'datatables.net-buttons-bs5/css/buttons.bootstrap5.min.css'
import 'datatables.net-responsive-bs5/css/responsive.bootstrap5.min.css'
import '@fortawesome/fontawesome-free/css/all.min.css'

const app = createApp(App)

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
