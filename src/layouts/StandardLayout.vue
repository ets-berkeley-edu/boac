<template>
  <b-container id="app" class="h-100 p-0" fluid>
    <b-row class="header" no-gutters>
      <b-col cols="auto" class="mr-auto m-3">
        <a
          id="skip-to-content-link"
          href="#content"
          class="sr-only sr-only-focusable"
          tabindex="2">Skip to main content</a>
        <router-link
          id="home-header"
          class="header-text"
          to="/home"
          tabindex="1">
          <span class="sr-only">Return to </span>Home
        </router-link>
      </b-col>
      <b-col cols="auto" class="p-0 mt-2">
        <HeaderMenu />
      </b-col>
    </b-row>
    <b-row class="row-content" no-gutters>
      <b-col class="sidebar" sm="3">
        <Sidebar />
      </b-col>
      <b-col id="content" class="body-text h-100 pb-2" sm="9">
        <div
          v-if="announcement && announcement.isPublished"
          class="service-announcement p-3 w-100">
          <span
            id="service-announcement-banner"
            aria-live="polite"
            role="alert">
            {{ announcement.text }}
          </span>
        </div>
        <div>
          <span
            v-if="srAlert"
            class="sr-only"
            aria-live="polite"
            role="alert">
            {{ srAlert }}
          </span>
          <router-view :key="stripAnchorRef($route.fullPath)"></router-view>
        </div>
      </b-col>
    </b-row>
    <b-row class="row-footer" no-gutters>
      <b-col class="sidebar" sm="3"></b-col>
      <b-col sm="9">
        <Footer v-if="!loading" class="mb-3 ml-3 mt-5" />
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import Context from '@/mixins/Context';
import Footer from '@/components/Footer';
import HeaderMenu from '@/components/HeaderMenu';
import Loading from '@/mixins/Loading';
import Sidebar from '@/components/sidebar/Sidebar';
import Util from '@/mixins/Util';

export default {
  name: 'StandardLayout',
  components: {
    Footer,
    HeaderMenu,
    Sidebar
  },
  mixins: [Context, Loading, Util],
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
}
.header {
  background-color: #3b7ea5;
}
.row-content {
  min-height: 82%;
}
.row-footer {
  min-height: 18%;
}
.service-announcement {
  background-color: #f0ad4e;
  font-weight: 500;
}
.sidebar {
  background-color: #125074;
}
</style>
