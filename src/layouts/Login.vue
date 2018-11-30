<template>
  <div class="background-blue-sky">
    <div class="splash-container">
      <div class="splash-cell-stripe"></div>
      <div class="avatar-container">
        <img class="avatar-airplane" :src="baseUrl + '/static/app/splash/airplane.svg'">
      </div>
      <div class="splash-cell-sign-in">
        <form @submit.prevent="logIn">
          <b-btn id="splash-sign-in"
                 class="splash-btn-sign-in"
                 v-on:click="logIn"
                 variant="primary"
                 placement="top-left">Sign In</b-btn>
        </form>
        <div class="splash-contact-us">
          Questions or feedback? Contact us at <a :href="'mailto:' + supportEmailAddress">{{ supportEmailAddress }}</a>
        </div>
        <form @submit.prevent="logInDevAuth()" v-if="devAuthEnabled">
          <div class="flex-container splash-dev-auth">
            <div>
              <input id="dev-auth-uid"
                     class="splash-form-input"
                     v-model="devAuth.uid"
                     type="text"
                     placeholder="UID"
                     autofocus
                     required
                     size="10">
            </div>
            <div>
              <input id="dev-auth-password"
                     autocomplete="none"
                     class="splash-form-input"
                     v-model="devAuth.password"
                     type="password"
                     placeholder="Password"
                     required
                     size="10">
            </div>
            <div>
              <b-btn id="dev-auth-submit"
                     class="splash-btn-dev-auth"
                     variant="primary"
                     type="submit">DevAuth!</b-btn>
            </div>
          </div>
        </form>
      </div>
      <div class="splash-box-container">
        <div class="splash-cell-header">
          <h1 class="splash-text-header">BOAC</h1>
        </div>
      </div>
      <div class="splash-cell-copyright">
        <span class="splash-text-copyright">&copy; 2018 The Regents of the University of California</span>
      </div>
    </div>
  </div>
</template>

<script>
import _ from 'lodash';
import { devAuthLogIn, getCasLoginURL } from '@/api/user';
import router from '@/router';
import store from '@/store';

export default {
  name: 'Login',
  data: () => ({
    devAuth: {
      uid: null,
      password: null
    }
  }),
  computed: {
    supportEmailAddress: () =>
      _.get(store.getters.config, 'supportEmailAddress'),
    devAuthEnabled: () => _.get(store.getters.config, 'devAuthEnabled'),
    baseUrl: () => store.state.apiBaseUrl
  },
  methods: {
    logIn() {
      getCasLoginURL().then(data => {
        window.location = data.casLoginUrl;
      });
    },
    logInDevAuth() {
      return devAuthLogIn(this.devAuth.uid, this.devAuth.password).then(() => {
        router.push({ path: 'home' });
      });
    }
  }
};
</script>

<style scoped>
</style>
