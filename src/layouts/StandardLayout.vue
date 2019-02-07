<template>
  <div id="app" class="index-container">
    <a href="#content"
       id="skip-to-content-link"
       class="sr-only sr-only-focusable"
       tabindex="2">Skip to main content</a>
    <div class="index-container-header">
      <div class="header-container">
        <div class="header-text">
          <router-link to="/home"
                       id="home-header"
                       tabindex="1"><span class="sr-only">Return to </span>Home</router-link>
        </div>
        <div><HeaderMenu/></div>
      </div>
    </div>
    <div class="index-container-body">
      <div class="index-container-sidebar">
        <Sidebar/>
      </div>
      <div class="index-container-content">
        <div id="content" class="body-text">
          <!-- The ':key' attribute forces component reload when same route is requested with diff id in path. -->
          <router-view :key="stripAnchorRef($route.fullPath)"></router-view>
        </div>
        <Footer v-if="!loading"/>
      </div>
    </div>
  </div>
</template>

<script>
import Footer from '@/components/Footer';
import HeaderMenu from '@/components/HeaderMenu';
import Loading from '@/mixins/Loading';
import Sidebar from '@/components/sidebar/Sidebar';
import Util from '@/mixins/Util';

export default {
  name: 'StandardLayout',
  mixins: [Loading, Util],
  components: {
    Footer,
    HeaderMenu,
    Sidebar
  },
  created() {
    this.putFocusNextTick('home-header');
  },
  methods: {
    stripAnchorRef(fullPath) {
      return this.split(fullPath, '#', 1)[0];
    }
  }
};
</script>

<style scoped>
.body-text {
  font-size: 16px;
  height: 100%;
  line-height: 1.4em;
}
.header-container {
  align-items: center;
  display: flex;
  height: 56px;
  justify-content: space-between;
}
.header-container div {
  margin-left: 20px;
  -webkit-flex: 1 0 0;
  flex: 1 0 0;
}
.header-container div:last-child {
  flex-grow: 0;
}
.header-container div:last-child > span {
  float: right;
}
.header-text {
  font-size: 16px;
  color: #fff;
}
.header-text a:link,
.header-text a:visited {
  color: #fff;
  text-decoration: none;
  border: 0;
  -moz-outline-style: none;
}
.header-text a:hover,
.header-text a:focus,
.header-text a:active {
  color: #ddd;
}
.header-text h1 {
  font-size: inherit;
  font-weight: inherit;
  margin: 0;
}
.index-container {
  height: 100%;
  margin: 0;
  padding: 0;
}
.index-container-content {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: 100%;
}
.index-container-body {
  display: flex;
  flex-direction: row;
  min-height: 100%;
}
.index-container-header {
  background-color: #3b7ea5;
}
.index-container-sidebar {
  background-color: #125074;
  flex: 0 0 230px;
  min-height: 100%;
}
</style>
