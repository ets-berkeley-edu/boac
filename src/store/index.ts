import cohort from '@/store/modules/cohort';
import cohortEditSession from '@/store/modules/cohort-edit-session';
import context from '@/store/modules/context';
import curated from '@/store/modules/curated';
import note from '@/store/modules/note';
import noteEditSession from '@/store/modules/note-edit-session';
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
    note,
    noteEditSession,
    user
  },
  strict: process.env.NODE_ENV !== 'production'
});
