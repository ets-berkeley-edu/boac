<template>
  <b-row class="header" no-gutters>
    <b-col cols="auto" class="mr-auto mb-3 ml-2 mt-3">
      <a
        id="skip-to-content-link"
        href="#content"
        class="sr-only"
      >
        Skip to main content
      </a>
      <div class="font-size-16 header-text pl-2 text-white" role="banner">
        <div v-if="$_.startsWith($route.path, '/home')">
          <span class="font-weight-bolder">UC Berkeley</span>
          Online Advising
        </div>
        <router-link
          v-if="!$_.startsWith($route.path, '/home')"
          id="home-header"
          to="/"
        >
          <span class="font-weight-bolder">UC Berkeley</span>
          Online Advising
        </router-link>
      </div>
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
