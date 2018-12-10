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
          <router-view></router-view>
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
import DisplayError from '@/components/DisplayError.vue';
import HeaderMenu from '@/components/HeaderMenu.vue';
import Sidebar from '@/components/sidebar/Sidebar.vue';

export default {
  name: 'App',
  components: {
    DisplayError,
    HeaderMenu,
    Sidebar
  }
};
</script>
