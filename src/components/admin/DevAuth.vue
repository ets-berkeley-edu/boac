<template>
  <form @submit.prevent="logInDevAuth()">
    <b-modal v-model="showError"
             @hidden="error = null"
             aria-label="Error"
             hide-header
             hide-backdrop
             return-focus="#dev-auth-uid"
             ok-only>
      <span role="alert" aria-live="passive">{{ error }}</span>
    </b-modal>
    <div class="flex-container splash-dev-auth">
      <div>
        <input id="dev-auth-uid"
               class="splash-form-input"
               autofocus
               placeholder="UID"
               v-model="uid"
               type="text"
               aria-required="true"
               aria-label="Input UID of an authorized user"
               :aria-invalid="showError"
               size="8">
      </div>
      <div class="ml-1">
        <input id="dev-auth-password"
               class="splash-form-input"
               placeholder="Password"
               v-model="password"
               type="password"
               aria-required="true"
               aria-label="Password"
               :aria-invalid="!!password"
               autocomplete="none"
               size="8">
      </div>
      <div class="ml-1">
        <b-btn id="dev-auth-submit"
               class="splash-btn-dev-auth btn-primary-color-override"
               variant="primary"
               aria-label="Log in to BOAC with dev-auth"
               type="submit">DevAuth!</b-btn>
      </div>
    </div>
  </form>
</template>

<script>
import _ from 'lodash';
import router from '@/router';
import store from '@/store';
import { devAuthLogIn } from '@/api/auth';

export default {
  name: 'DevAuth',
  data: () => ({
    uid: null,
    password: null,
    error: null,
    showError: false
  }),
  methods: {
    logInDevAuth() {
      let uid = _.trim(this.uid);
      let password = _.trim(this.password);
      if (uid && password) {
        devAuthLogIn(uid, password)
          .then(data => {
            let status = _.get(data, 'response.status');
            if (status && status !== 200) {
              this.reportError(
                status < 404 ? 'Invalid credentials' : 'Uh oh, system error!'
              );
            } else if (data.isAuthenticated) {
              store.dispatch('user/userAuthenticated').then(() => {
                router.push({ path: '/home' });
              });
            } else {
              this.reportError(
                'Unauthorized. Please contact us for assistance.'
              );
            }
          })
          .catch(err => {
            this.reportError(err.message || 'Invalid credentials');
          });
      } else {
        this.reportError(
          this.uid ? 'Password required' : 'UID and password required'
        );
      }
    },
    reportError(message) {
      this.error = message;
      this.showError = true;
    }
  },
  watch: {
    uid: function() {
      this.error = null;
    },
    password: function() {
      this.error = null;
    }
  }
};
</script>

<style scoped>
button {
  background-color: #3b80bf;
}
</style>
