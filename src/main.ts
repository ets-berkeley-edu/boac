import 'bootstrap-vue/dist/bootstrap-vue.min.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'v-calendar/lib/v-calendar.min.css';
import _ from 'lodash';
import App from './App.vue';
import axios from 'axios';
import BootstrapVue from 'bootstrap-vue';
import CKEditor from '@ckeditor/ckeditor5-vue';
import filters from './filters';
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
import { fas } from '@fortawesome/free-solid-svg-icons'
import { faSpinner } from "@fortawesome/free-solid-svg-icons/faSpinner";
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

library.add(fas, faSpinner);
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
