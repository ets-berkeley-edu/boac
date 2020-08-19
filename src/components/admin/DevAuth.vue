<template>
  <form @submit.prevent="logIn">
    <div class="flex-container dev-auth">
      <div>
        <input
          id="dev-auth-uid"
          v-model="uid"
          class="form-input"
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
          :aria-invalid="!!password"
          class="form-input"
          placeholder="Password"
          type="password"
          aria-required="true"
          aria-label="Password"
          autocomplete="off"
          size="8">
      </div>
      <div class="ml-1">
        <b-btn
          id="dev-auth-submit"
          class="btn-dev-auth btn-primary-color-override"
          variant="primary"
          aria-label="Log in to BOA with dev-auth"
          type="submit">
          DevAuth!
        </b-btn>
      </div>
    </div>
  </form>
</template>

<script>
import Context from '@/mixins/Context';
import Util from '@/mixins/Util';
import { devAuthLogIn } from '@/api/auth';

export default {
  name: 'DevAuth',
  mixins: [Context, Util],
  props: {
    reportError: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    uid: null,
    password: null
  }),
  created() {
    this.putFocusNextTick('dev-auth-uid');
  },
  methods: {
    logIn() {
      let uid = this.trim(this.uid);
      let password = this.trim(this.password);
      if (uid && password) {
        devAuthLogIn(uid, password).then(user => {
          if (user.isAuthenticated) {
            const redirect = this.get(this.$router, 'currentRoute.query.redirect');
            this.$router.push({ path: redirect || '/home' }, this.noop);
          } else {
            this.reportError('Sorry, user is not authorized to use BOA.');
          }
        });
      } else if (uid) {
        this.reportError('Password required');
        this.putFocusNextTick('dev-auth-password');
      } else {
        this.reportError('Both UID and password are required');
        this.putFocusNextTick('dev-auth-uid');
      }
    }
  }
};
</script>

<style scoped>
button {
  background-color: #3b80bf;
}
.btn-dev-auth {
  height: 26px;
  padding: 0 !important;
  width: 80px;
}
.dev-auth {
  justify-content: center;
  padding-top: 10px;
  white-space: nowrap;
}
.form-input {
  padding-right: 5px;
}
</style>
