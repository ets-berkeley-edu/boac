<template>
  <div id="app">
    <b-container fluid>
      <b-row class="toolbar">
        <b-col sm="8"><a :href="homeAddress">Home</a></b-col>
        <b-col sm="4"><HeaderMenu/></b-col>
      </b-row>
      <b-row>
        <b-col class="sidebar-container">
          <div class="nav-container">
            <Sidebar/>
          </div>
        </b-col>
        <b-col>
          <DisplayError/>
          <router-view></router-view>
        </b-col>
        <b-col>
          <b-row>
            <b-col sm="8"><img src="@/assets/uc-berkeley-logo.svg"/></b-col>
            <b-col sm="4">&copy; 2018 The Regents of the University of California</b-col>
          </b-row>
        </b-col>
      </b-row>
    </b-container>
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
  max-width: 230px;
}
.toolbar {
  font-size: 16px;
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
