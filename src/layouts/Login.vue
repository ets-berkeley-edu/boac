<template>
  <div class="background-blue-sky">
    <div class="splash-container">
      <div class="splash-cell-stripe"></div>
      <div class="avatar-container">
        <img class="avatar-airplane"
             :src="`${baseUrl}/static/app/splash/airplane.svg`">
      </div>
      <div class="splash-cell-sign-in">
        <form @submit.prevent="logIn">
          <b-btn id="splash-sign-in"
                 class="splash-btn-sign-in"
                 autofocus
                 @click.prevent="logIn"
                 variant="primary"
                 placement="top-left">Sign In</b-btn>
          <b-popover target="dev-auth-uid"
                     placement="topright"
                     :show="error.target === 'logIn'"
                     :title="error.title || 'Error'"
                     triggers="hover focus"
                     :content="error.message">
          </b-popover>
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
                     @change="clearError"
                     type="text"
                     placeholder="UID"
                     size="10">
              <b-popover target="dev-auth-uid"
                         placement="topright"
                         :show="error.target === 'devAuth'"
                         :title="error.title || 'Error'"
                         triggers="hover focus"
                         :content="error.message">
              </b-popover>
            </div>
            <div>
              <input id="dev-auth-password"
                     autocomplete="none"
                     class="splash-form-input"
                     v-model="devAuth.password"
                     @change="clearError"
                     @click.prevent="logInDevAuth()"
                     type="password"
                     placeholder="Password"
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
import AppConfig from '@/mixins/AppConfig';
import router from '@/router';
import store from '@/store';
import { devAuthLogIn, getCasLoginURL } from '@/api/user';

export default {
  name: 'Login',
  mixins: [AppConfig],
  data: () => ({
    devAuth: {
      uid: null,
      password: null
    },
    error: null
  }),
  created() {
    this.clearError();
  },
  methods: {
    clearError() {
      this.error = {
        title: null,
        message: null,
        target: null
      };
    },
    logIn() {
      getCasLoginURL().then(data => {
        window.location.href = data.casLoginUrl;
      });
    },
    logInDevAuth() {
      if (this.devAuth.uid && this.devAuth.password) {
        devAuthLogIn(this.devAuth.uid, this.devAuth.password)
          .then(status => {
            if (status.isAuthenticated) {
              store.commit('userAuthenticated');
              router.push({ path: '/' });
            } else {
              this.error = {
                message:
                  status.get('error') ||
                  'Sorry, you are unauthorized to use BOAC. Please contact us for assistance.',
                hide: false
              };
            }
          })
          .catch(err => {
            this.error = {
              message:
                err.message ||
                'Sorry, we were unable to authenticate your credentials',
              hide: false
            };
          });
      }
    }
  }
};
</script>
