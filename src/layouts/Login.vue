<template>
  <div class="background-blue-sky fill-viewport">
    <div class="splash-container">
      <div class="splash-cell-stripe"></div>
      <div class="avatar-container">
        <img class="avatar-airplane"
             :src="`${baseUrl}/static/app/splash/airplane.svg`">
      </div>
      <div class="splash-cell-sign-in">
        <form @submit.prevent="logIn()">
          <b-btn id="splash-sign-in"
                 class="btn-sign-in"
                 aria-label="Log in to BOAC"
                 @click.stop="logIn()"
                 variant="primary"
                 tabindex="0"
                 placement="top-left">Sign In</b-btn>
        </form>
        <div class="splash-contact-us">
          Questions or feedback? Contact us at
          <a :href="`mailto:${supportEmailAddress}`"
             aria-label="BOAC support email address"
             target="_blank">{{ supportEmailAddress }}</a>
        </div>
        <DevAuth v-if="devAuthEnabled"/>
      </div>
      <div class="splash-box-container">
        <div class="splash-cell-header">
          <h1>BOAC</h1>
        </div>
      </div>
      <div class="splash-cell-copyright pt-2">
        <span class="splash-text-copyright">&copy; 2018 The Regents of the University of California</span>
      </div>
    </div>
  </div>
</template>

<script>
import AppConfig from '@/mixins/AppConfig';
import DevAuth from '@/components/admin/DevAuth.vue';
import { getCasLoginURL } from '@/api/auth';

export default {
  name: 'Login',
  mixins: [AppConfig],
  components: {
    DevAuth
  },
  methods: {
    logIn() {
      getCasLoginURL().then(data => {
        window.location.href = data.casLoginUrl;
      });
    }
  }
};
</script>

<style scoped>
h1 {
  color: #0275d8;
  font-weight: 200;
  font-size: 81px;
  letter-spacing: 8px;
  padding-top: 14px;
}
.btn-sign-in {
  height: 50px;
  width: 256px;
  font-size: 20px;
  top: 4.7em;
}
button {
  background-color: #3b80bf;
}
</style>
