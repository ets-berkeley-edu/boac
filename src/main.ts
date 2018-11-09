import Vue from 'vue';
import App from './App.vue';
import axios from 'axios';
import BootstrapVue from 'bootstrap-vue';
import router from './router';
import store from './store';

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

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app');
