<template>
  <div id="app">
    <v-app>
      <v-toolbar color="#3b7ea5">
        <v-toolbar-title v-on:click="goHome()" class="white--text">Home</v-toolbar-title>
        <v-spacer></v-spacer>
        <HeaderMenu/>
      </v-toolbar>
      <v-layout row>
        <v-flex shrink>
          <v-navigation-drawer dark permanent>
            <Sidebar/>
          </v-navigation-drawer>
        </v-flex>
        <v-layout column align-start justify-space-between>
          <v-flex class="footer">
            <DisplayError/>
            <router-view></router-view>
          </v-flex>
          <v-footer class="footer-container">
            <v-layout row justify-space-between align-end>
              <v-flex class="text-sm-left">
                <img src="@/assets/uc-berkeley-logo.svg"/>
              </v-flex>
              <v-flex class="text-xs-right">
                &copy; 2018 The Regents of the University of California
              </v-flex>
            </v-layout>
          </v-footer>
        </v-layout>
      </v-layout>
    </v-app>
  </div>
</template>

<script>
import DisplayError from './components/DisplayError.vue';
import HeaderMenu from './components/HeaderMenu.vue';
import Sidebar from './components/Sidebar.vue';
import store from '@/store';

export default {
  name: 'App',
  components: {
    DisplayError,
    HeaderMenu,
    Sidebar
  },
  methods: {
    goHome() {
      window.location.href = store.state.apiBaseUrl;
    }
  }
};
</script>

<style scoped>
.footer-container {
  width: 100%;
}
</style>
