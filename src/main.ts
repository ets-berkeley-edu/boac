import 'bootstrap-vue/dist/bootstrap-vue.css';
import 'bootstrap/dist/css/bootstrap.css';
import _ from 'lodash';
import App from './App.vue';
import axios from 'axios';
import BootstrapVue from 'bootstrap-vue';
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
  let status = error.response.status;
  if (_.includes([401, 403, 404], status)) {
    router.push({ path: '/404' });
  } else {
    store.dispatch('context/reportError', {
      message: error.message,
      text: error.response.text,
      status: status,
      stack: error.stack
    });
  }
  return Promise.reject(error);
});

Vue.config.productionTip = false;
Vue.use(BootstrapVue);
Vue.use(require('vue-lodash'));

HighchartsMore(Highcharts);
Vue.use(VueHighcharts, { Highcharts });

store.dispatch('context/loadConfig').then(response => {
  let googleAnalyticsId = _.get(response, 'googleAnalyticsId');
  if (googleAnalyticsId) {
    Vue.use(VueAnalytics, {
      id: googleAnalyticsId,
      checkDuplicatedScript: true
    });
  }
});

// Filters and directives
_.each(filters, (filter, name) => Vue.filter(name, filter));

// Emit, and listen for, events via hub
Vue.prototype.$eventHub = new Vue();

Vue.use(routerHistory);
router.afterEach(writeHistory);

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app');
