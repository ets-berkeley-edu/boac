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
        <Footer v-if="!loading"/>
      </div>
    </div>
  </div>
</template>

<script>
import DisplayError from '@/components/util/DisplayError';
import Footer from '@/components/Footer';
import HeaderMenu from '@/components/HeaderMenu';
import Loading from '@/mixins/Loading';
import Sidebar from '@/components/sidebar/Sidebar';

export default {
  name: 'StandardLayout',
  mixins: [Loading],
  components: {
    DisplayError,
    Footer,
    HeaderMenu,
    Sidebar
  }
};
</script>
