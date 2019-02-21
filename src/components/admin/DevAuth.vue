<template>
  <form @submit.prevent="logInDevAuth()">
    <div class="flex-container splash-dev-auth">
      <div>
        <input
          id="dev-auth-uid"
          v-model="uid"
          class="splash-form-input"
          autofocus
          placeholder="UID"
          type="text"
          aria-required="true"
          aria-label="Input UID of an authorized user"
          size="8">
      </div>
      <div class="ml-1">
        <input
          id="dev-auth-password"
          v-model="password"
          class="splash-form-input"
          placeholder="Password"
          type="password"
          aria-required="true"
          aria-label="Password"
          :aria-invalid="!!password"
          autocomplete="off"
          size="8">
      </div>
      <div class="ml-1">
        <b-btn
          id="dev-auth-submit"
          class="splash-btn-dev-auth btn-primary-color-override"
          variant="primary"
          aria-label="Log in to BOAC with dev-auth"
          type="submit">
          DevAuth!
        </b-btn>
      </div>
    </div>
  </form>
</template>

<script>
import Context from '@/mixins/Context';
import router from '@/router';
import UserMetadata from "@/mixins/UserMetadata";
import Util from '@/mixins/Util';
import { devAuthLogIn } from '@/api/auth';

export default {
  name: 'DevAuth',
  mixins: [Context, UserMetadata, Util],
  data: () => ({
    uid: null,
    password: null
  }),
  methods: {
    logInDevAuth() {
      let uid = this.trim(this.uid);
      let password = this.trim(this.password);
      if (uid && password) {
        devAuthLogIn(uid, password)
          .then(data => {
            // Auth errors will be caught by axios.interceptors; see error reporting in the file 'main.ts'.
            if (data.isAuthenticated) {
              this.userAuthenticated().then(() => router.push({ path: router.currentRoute.query.redirect || '/home' }));
            }
          });
      } else {
        this.reportError({ message: this.uid ? 'Password required' : 'UID and password required' });
      }
    }
  }
};
</script>

<style scoped>
button {
  background-color: #3b80bf;
}
.splash-btn-dev-auth {
  height: 26px;
  padding: 0 !important;
  width: 80px;
}
.splash-dev-auth {
  justify-content: center;
  padding-top: 10px;
  white-space: nowrap;
}
.splash-form-input {
  padding-right: 5px;
}
</style>
