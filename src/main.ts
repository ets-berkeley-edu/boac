import 'bootstrap-vue/dist/bootstrap-vue.css';
import 'bootstrap/dist/css/bootstrap.css';
import { format as formatDate, parse as parseDate } from 'date-fns';
import App from './App.vue';
import axios from 'axios';
import BootstrapVue from 'bootstrap-vue';
import router from './router';
import store from './store';
import Vue from 'vue';

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

Vue.filter('date', (dateString: string, format: string = 'MMM dd, YYYY') => {
  let date = parseDate(dateString);
  return formatDate(date, format);
});
Vue.filter('lowercase', (str: string) => {
  return str.toLowerCase();
});
Vue.filter('pluralize', (noun: string, count: number, substitutions = {}) => {
  return (
    `${substitutions[count] || count} ` + (count !== 1 ? `${noun}s` : noun)
  );
});
Vue.filter('round', function(value, decimals) {
  return Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals);
});
Vue.filter(
  'variablePrecisionNumber',
  (value, minPrecision, maxPrecision) =>
    `TODO: ${value}, ${minPrecision}, ${maxPrecision}`
);
// Emit, and listen for, events via hub
Vue.prototype.$eventHub = new Vue();

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app');
