import _ from 'lodash';
import store from "@/store";
import Vue from 'vue';

export function gaTrackUserSessionStart(user: any) {
  if (Vue.prototype.$ga) {
    let googleAnalyticsId = store.getters['context/googleAnalyticsId'];
    if (googleAnalyticsId) {
      Vue.prototype.$ga.set('userId', user.uid);
      const dept_code = user.isAdmin
        ? 'ADMIN'
        : _.keys(user.departments)[0];
      if (dept_code) {
        Vue.prototype.$ga.set('dimension1', dept_code);
      }
    }
  }
}
