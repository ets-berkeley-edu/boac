import cohort from '@/store/modules/cohort';
import context from '@/store/modules/context';
import curated from '@/store/modules/curated';
import user from '@/store/modules/user';
import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    cohort,
    context,
    curated,
    user
  },
  strict: process.env.NODE_ENV !== 'production'
});
