<template>
  <b-row class="header" no-gutters>
    <b-col cols="auto" class="mr-auto m-3">
      <a
        id="skip-to-content-link"
        href="#content"
        class="sr-only sr-only-focusable"
        tabindex="0">Skip to main content</a>
      <router-link
        id="home-header"
        class="header-text"
        to="/"
        tabindex="0">
        <span class="sr-only">Return to </span>Home
      </router-link>
    </b-col>
    <b-col cols="auto" class="p-0 mt-2">
      <HeaderMenu />
    </b-col>
  </b-row>
</template>

<script>
import HeaderMenu from '@/components/HeaderMenu'

export default {
  name: 'StandardHeaderLayout',
  components: {
    HeaderMenu
  }
}
</script>

<style scoped>
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
</style>
