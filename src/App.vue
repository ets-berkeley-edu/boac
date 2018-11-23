<template>
  <div id="app">
    <v-app>
      <v-toolbar class="toolbar">
        <v-toolbar-title><a :href="homeAddress">Home</a></v-toolbar-title>
        <v-spacer></v-spacer>
        <HeaderMenu/>
      </v-toolbar>
      <v-layout row>
        <v-flex shrink class="sidebar-container font-weight-medium">
          <v-navigation-drawer dark permanent class="nav-container">
            <Sidebar/>
          </v-navigation-drawer>
        </v-flex>
        <v-layout column align-start justify-space-between ml-2 mt-2>
          <v-content app>
            <DisplayError/>
            <router-view></router-view>
          </v-content>
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
import Sidebar from './components/sidebar/Sidebar.vue';
import store from '@/store';

export default {
  name: 'App',
  components: {
    DisplayError,
    HeaderMenu,
    Sidebar
  },
  data: () => ({
    homeAddress: store.state.apiBaseUrl
  })
};
</script>

<style scoped>
.footer-container {
  width: 100%;
}
.nav-container {
  background-color: #125074;
}
.sidebar-container {
  width: 230px;
}
.toolbar {
  font-size: 16px;
  color: #fff;
  background-color: #3b7ea5;
}
.toolbar a:link,
.toolbar a:visited {
  color: #fff;
  text-decoration: none;
  border: 0;
  -moz-outline-style: none;
}
.toolbar a:hover,
.toolbar a:focus,
.toolbar a:active {
  color: #ddd;
}
</style>

<style>
.has-error {
  color: red;
}
.no-wrap {
  white-space: nowrap;
}
.page-section-header {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 10px;
}
.page-section-header-sub {
  font-size: 18px;
  font-weight: bold;
}
</style>
