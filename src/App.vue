<template>
  <div class="index-container">
    <a href="#content"
       id="skip-to-content-link"
       class="sr-only">Skip To Content</a>
    <div class="header-container">
      <Header/>
    </div>
    <div class="body-container">
      <div class="sidebar-container">
        <sidebar></sidebar>
      </div>
      <div class="content">
        <div id="content">
          <display-error/>
          <router-view/>
        </div>
        <div class="footer-container">
          <Footer/>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import DisplayError from './components/DisplayError.vue';
import Footer from './components/Footer.vue';
import Header from './components/Header.vue';
import Sidebar from './components/Sidebar.vue';

export default {
  name: 'App',
  components: {
    DisplayError,
    Footer,
    Header,
    Sidebar
  }
};
</script>

<style scoped lang="scss">
.content {
  flex: 1;
  font-size: 16px;
  line-height: 1.4em;
  min-height: 100%;
}
.index-container {
  height: 100%;
  margin: 0;
  padding: 0;
}
.body-container {
  display: flex;
  flex-direction: row;
  min-height: 100%;
}
.footer-container {
  margin: 20px 0 70px 0;
  width: 100%;
}
.header-container {
  background-color: #3b7ea5;
}
.sidebar-container {
  background-color: #125074;
  flex: 0 0 230px;
  min-height: 100%;
}
</style>
