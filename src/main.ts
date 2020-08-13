import 'bootstrap-vue/dist/bootstrap-vue.min.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'v-calendar/lib/v-calendar.min.css';
import _ from 'lodash';
import App from './App.vue';
import axios from 'axios';
import BootstrapVue from 'bootstrap-vue';
import CKEditor from '@ckeditor/ckeditor5-vue';
import core from './core';
import Highcharts from 'highcharts';
import HighchartsMore from 'highcharts/highcharts-more';
import moment from 'moment-timezone';
import router from './router';
import store from './store';
import VDatePicker from 'v-calendar';
import Vue from 'vue';
import VueHighcharts from 'vue-highcharts';
import VueMoment from 'vue-moment';
import { routerHistory, writeHistory } from 'vue-router-back-button';
import { library } from '@fortawesome/fontawesome-svg-core'
import { far } from '@fortawesome/free-regular-svg-icons'
import { fas } from '@fortawesome/free-solid-svg-icons'
import { faSpinner } from "@fortawesome/free-solid-svg-icons/faSpinner";
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

library.add(far, fas, faSpinner);
Vue.component('font-awesome', FontAwesomeIcon);

// Allow cookies in Access-Control requests
axios.defaults.withCredentials = true;

Vue.config.productionTip = false;
Vue.use(BootstrapVue);
Vue.use(CKEditor);
Vue.use(VDatePicker);
Vue.use(require('vue-lodash'));
Vue.use(VueMoment, { moment });

HighchartsMore(Highcharts);
Vue.use(VueHighcharts, { Highcharts });

Vue.directive('accessibleGrade', {
  bind: (el, binding) => el.innerHTML = binding.value && binding.value.replace('-', '&minus;').replace('+', '&plus;')
});

// Emit, and listen for, events via hub
Vue.prototype.$eventHub = new Vue();

// Lodash
Vue.prototype.$_ = _;

Vue.use(routerHistory);
router.afterEach(writeHistory);

const apiBaseUrl = process.env.VUE_APP_API_BASE_URL;

axios.interceptors.response.use(response => response, function(error) {
  if (_.get(error, 'response.status') === 401) {
    axios.get(`${apiBaseUrl}/api/profile/my`).then(response => {
      Vue.prototype.$currentUser = response.data;
      Vue.prototype.$core.initializeCurrentUser().then(router.push({ path: '/login' }).catch(() => null));
    });
  }
  return Promise.reject(error);
});

axios.get(`${apiBaseUrl}/api/profile/my`).then(response => {
  Vue.prototype.$currentUser = response.data;

  axios.get(`${apiBaseUrl}/api/config`).then(response => {
    Vue.prototype.$config = response.data;
    Vue.prototype.$config.apiBaseUrl = apiBaseUrl;
    Vue.prototype.$config.isVueAppDebugMode = _.trim(process.env.VUE_APP_DEBUG).toLowerCase() === 'true';

    // Mount BOA
    new Vue({
      router,
      store,
      render: h => h(App)
    }).$mount('#app');

    if (Vue.prototype.$config.pingFrequency) {
      // Keep session alive with periodic requests
      setInterval(() => axios.get(`${apiBaseUrl}/api/ping`), Vue.prototype.$config.pingFrequency);
    }
    // The 'core' functions strictly manage state changes in $currentUser and other "prototype" objects.
    // For example, core functions might be invoked after a successful dev-auth login.
    Vue.prototype.$core = core;
    Vue.prototype.$core.initializeCurrentUser().then(_.noop);
    Vue.prototype.$core.mountGoogleAnalytics().then(_.noop);
    // The following non-core function(s) do not involve "prototype" objects.
    store.dispatch('context/loadServiceAnnouncement');
  });
});
