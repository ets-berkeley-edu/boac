<template>
  <div class="background-blue-sky fill-viewport">
    <span
      v-if="screenReaderAlert"
      class="sr-only"
      aria-live="polite"
      role="alert">
      {{ screenReaderAlert }}
    </span>
    <div class="splash-container">
      <div class="splash-cell-stripe"></div>
      <div class="avatar-container">
        <img src="@/assets/airplane.svg" alt="Airplane logo" class="avatar-airplane" />
      </div>
      <div class="splash-cell-sign-in" role="main">
        <form @submit.prevent="logIn()">
          <b-btn
            id="splash-sign-in"
            @click.stop="logIn()"
            class="btn-sign-in btn-primary-color-override"
            variant="primary"
            aria-label="Log in to BOA"
            tabindex="0"
            placement="top">
            Sign In
          </b-btn>
          <b-popover
            @hidden="onHidden"
            placement="top"
            target="splash-sign-in"
            triggers="focus">
            <span
              v-for="message in errorMessages"
              :key="message"
              v-html="message"
              class="has-error"
              aria-live="polite"></span>
          </b-popover>
        </form>
        <div class="splash-contact-us">
          Questions or feedback? Contact us at
          <a
            :href="`mailto:${supportEmailAddress}`"
            aria-label="BOA support email address"
            target="_blank">{{ supportEmailAddress }}<span class="sr-only"> (will open new browser tab)</span></a>
        </div>
        <DevAuth v-if="devAuthEnabled" />
      </div>
      <div class="splash-box-container" role="banner">
        <div class="splash-cell-header">
          <h1>BOA</h1>
        </div>
      </div>
      <div class="splash-cell-copyright pt-2" role="contentinfo">
        <span class="font-size-12 text-white">&copy; 2019 The Regents of the University of California</span>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import DevAuth from '@/components/admin/DevAuth';
import Util from '@/mixins/Util';
import { getCasLoginURL } from '@/api/auth';

export default {
  name: 'Login',
  components: {
    DevAuth
  },
  mixins: [Context, Util],
  data: () => ({
    errorMessages: undefined
  }),
  created() {
    this.errorCheck();
    this.$eventHub.$on('error-reported', () => this.errorCheck());
  },
  methods: {
    errorCheck() {
      if (this.size(this.errors)) {
        this.alertScreenReader('Login failed');
        this.errorMessages = this.map(this.errors, 'message');
        this.putFocusNextTick('splash-sign-in');
        this.clearAlertsInStore();
      }
    },
    logIn() {
      getCasLoginURL().then(data => window.location.href = data.casLoginUrl);
    },
    onHidden() {
      this.errorMessages = null;
    }
  }
};
</script>

<style scoped>
.avatar-airplane {
  background-color: #fff;
  border: 10px solid #0275d8;
  border-radius: 50px;
  object-fit: scale-down;
  width: 96px;
}
.avatar-container {
  align-items: center;
  display: flex;
  flex: 0 0 100px;
  position: absolute;
  top: 205px;
  left: 50%;
  transform: translate(-50%, -50%);
}
.background-blue-sky {
  background: url('~@/assets/blue-sky-background.jpg') no-repeat center center
    fixed;
  -webkit-background-size: cover;
  -moz-background-size: cover;
  -o-background-size: cover;
  background-size: cover;
}
.btn-sign-in {
  height: 50px;
  width: 256px;
  font-size: 20px;
  top: 4.7em;
}
.splash-box-container {
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.5);
  flex: 1;
  height: 360px;
  min-height: 360px;
  width: 320px;
  opacity: 0.8;
  padding: 0 25px 0 25px;
  z-index: -1;
}
.splash-cell-copyright {
  background-color: #3b80bf;
  height: 40px;
  width: 320px;
  padding-top: 10px;
  text-align: center;
  white-space: nowrap;
}
.splash-cell-header {
  padding-top: 40px;
  text-align: center;
}
.splash-cell-sign-in {
  position: absolute;
  top: 460px;
  left: 50%;
  text-align: center;
  transform: translate(-50%, -50%);
}
.splash-cell-stripe {
  background-color: #0275d8;
  height: 10px;
  width: 320px;
}
.splash-contact-us {
  padding: 20px 40px 10px 40px;
  width: 320px;
  text-align: left;
}
.splash-container {
  align-items: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 24em;
  padding-top: 200px;
  position: relative;
  z-index: 999;
}
button {
  background-color: #3b80bf;
}
h1 {
  color: #0275d8;
  font-weight: 200;
  font-size: 81px;
  letter-spacing: 8px;
  padding-top: 14px;
}
</style>
