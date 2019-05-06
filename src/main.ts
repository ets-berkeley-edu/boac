import 'bootstrap-vue/dist/bootstrap-vue.min.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import _ from 'lodash';
import App from './App.vue';
import axios from 'axios';
import BootstrapVue from 'bootstrap-vue';
import CKEditor from '@ckeditor/ckeditor5-vue';
import filters from './filters';
import Highcharts from 'highcharts';
import HighchartsMore from 'highcharts/highcharts-more';
import router from './router';
import store from './store';
import Vue from 'vue';
import VueAnalytics from 'vue-analytics';
import VueHighcharts from 'vue-highcharts';
import { routerHistory, writeHistory } from 'vue-router-back-button';

// Allow cookies in Access-Control requests
axios.defaults.withCredentials = true;
axios.interceptors.response.use(response => response, function(error) {
  let status = _.get(error, 'response.status') || 'Unknown';
  if (_.includes([404], status)) {
    router.push({ path: '/404' });
  } else {
    store.dispatch('context/reportError', {
      message: _.get(error.response, 'data.message') || error.message || `Request failed with status ${status}`,
      status: status
    });
  }
  return Promise.reject(error);
});

Vue.config.productionTip = false;
Vue.use(BootstrapVue);
Vue.use(CKEditor);
Vue.use(require('vue-lodash'));
Vue.use(require('vue-moment'));

HighchartsMore(Highcharts);
Vue.use(VueHighcharts, { Highcharts });

store.dispatch('context/loadConfig').then(response => {
  let googleAnalyticsId = _.get(response, 'googleAnalyticsId');
  if (googleAnalyticsId) {
    Vue.use(VueAnalytics, {
      id: googleAnalyticsId,
      debug: {
        // If debug.enabled is true then browser console gets GA debug info.
        enabled: false
      },
      router,
      checkDuplicatedScript: true
    });
  }
});

// Filters and directives
_.each(filters, (filter, name) => Vue.filter(name, filter));
Vue.directive('accessibleGrade', {
  bind: (el, binding) => el.innerHTML = binding.value && binding.value.replace('-', '&minus;').replace('+', '&plus;')
});

// Emit, and listen for, events via hub
Vue.prototype.$eventHub = new Vue();

Vue.use(routerHistory);
router.afterEach(writeHistory);

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app');
