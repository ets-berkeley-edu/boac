import cohort from '@/store/modules/cohort';
import cohortEditSession from '@/store/modules/cohort-edit-session';
import context from '@/store/modules/context';
import curated from '@/store/modules/curated';
import studentEditSession from '@/store/modules/student-edit-session';
import user from '@/store/modules/user';
import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    cohort,
    cohortEditSession,
    context,
    curated,
    studentEditSession,
    user
  },
  strict: process.env.NODE_ENV !== 'production'
});
