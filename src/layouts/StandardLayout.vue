<template>
  <div id="app" class="index-container">
    <a href="#content"
       id="skip-to-content-link"
       class="sr-only sr-only-focusable">Skip to main content</a>
    <div class="index-container-header">
      <div class="header-container">
        <div class="header-text"><router-link to="/home">Home</router-link></div>
        <div><HeaderMenu/></div>
      </div>
    </div>
    <div class="index-container-body">
      <div class="index-container-sidebar">
        <Sidebar/>
      </div>
      <div class="index-container-content">
        <div id="content" class="body-text">
          <DisplayError/>
          <!-- The ':key' attribute forces component reload when same route is requested with diff id in path. -->
          <router-view :key="$route.fullPath"></router-view>
        </div>
        <div class="index-container-footer">
          <hr class="footer-separator">
          <div class="footer-container">
            <div>
              <img src="@/assets/uc-berkeley-logo.svg"/>
            </div>
            <div class="footer-copyright">
              &copy; 2018 The Regents of the University of California
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import DisplayError from '@/components/util/DisplayError';
import HeaderMenu from '@/components/HeaderMenu';
import Sidebar from '@/components/sidebar/Sidebar';

export default {
  name: 'App',
  components: {
    DisplayError,
    HeaderMenu,
    Sidebar
  }
};
</script>

<style>
h1 {
  font-size: 24px;
  font-weight: bold;
  margin: 0 0 10px 0;
}
.b-dd-primary-override {
  background-color: #337ab7;
  border-color: #2e6da4;
  border-top-right-radius: 0.3em !important;
  border-bottom-right-radius: 0.3em !important;
  margin-left: 5px !important;
}
.b-dd-primary-override:hover,
.b-dd-primary-override:focus,
.b-dd-primary-override:active {
  background-color: #286090;
  border-color: #204d74;
}
.b-dd-item-override {
  color: #212529 !important;
}
</style>
