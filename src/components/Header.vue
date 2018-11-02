<template>
  <div class="header">
    <div class="logo">
      <legacy-link uri="/home">
        <i style="color: #0275d8" class="fas fa-plane-departure"></i>
      </legacy-link>
    </div>
    <div class="flex-row greeting" v-if="user">
      <div>Hello {{ user.uid }}</div>
      <div>
        [<b-link v-on:click="logOut()">Logout</b-link>]
      </div>
    </div>
  </div>
</template>

<script>
import { getCasLogoutURL } from '@/api/user';
import LegacyLink from '@/components/links/legacy.vue';
import store from '@/store';

export default {
  name: 'Header',
  components: {
    LegacyLink
  },
  data() {
    return {
      homeUrl: null,
      user: null
    };
  },
  created() {
    this.homeUrl = store.state.apiBaseUrl + '/home';
    this.user = store.getters.user;
  },
  methods: {
    logOut() {
      getCasLogoutURL().then(data => {
        window.location.href = data.casLogoutURL;
      });
    }
  }
};
</script>

<style scoped lang="scss">
.breadcrumb span {
  padding: 5px;
}
.header {
  display: flex;
  justify-content: space-between;
}
.logo {
  padding-top: 10px;
}
.greeting {
  padding-top: 15px;
}
.greeting div {
  padding-left: 10px;
}
</style>
