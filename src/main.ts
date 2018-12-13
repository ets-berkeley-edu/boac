import './filters';
import 'bootstrap-vue/dist/bootstrap-vue.css';
import 'bootstrap/dist/css/bootstrap.css';
import _ from 'lodash';
import App from './App.vue';
import axios from 'axios';
import BootstrapVue from 'bootstrap-vue';
import router from './router';
import store from './store';
import Vue from 'vue';
import VueAnalytics from 'vue-analytics';
import VueHighcharts from 'vue-highcharts';
import { format as formatDate, parse as parseDate } from 'date-fns';

// Allow cookies in Access-Control requests
axios.defaults.withCredentials = true;
axios.interceptors.response.use(response => response, function(error) {
  store.commit('reportError', {
    message: error.message,
    text: error.response.text,
    status: error.response.status,
    stack: error.stack
  });
  return Promise.reject(error);
});

Vue.config.productionTip = false;
Vue.use(BootstrapVue);
Vue.use(require('vue-lodash'));
Vue.use(VueHighcharts);
Vue.use(VueAnalytics, {
  id: store.dispatch('context/loadConfig').then(response => {
    return _.get(response, 'googleAnalyticsId');
  }),
  checkDuplicatedScript: true
});

// Emit, and listen for, events via hub
Vue.prototype.$eventHub = new Vue();

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app');
