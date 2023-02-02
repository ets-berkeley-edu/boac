<template>
  <div class="d-flex justify-content-between min-width-100 p-2">
    <div class="align-self-center flex-grow-1">
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
    </div>
    <div class="align-self-center">
      <BasicSearch />
    </div>
    <div class="align-self-center">
      <HeaderMenu />
    </div>
  </div>
</template>

<script>
import BasicSearch from '@/components/header/BasicSearch'
import HeaderMenu from '@/components/header/HeaderMenu'

export default {
  name: 'StandardHeaderLayout',
  components: {
    BasicSearch,
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
</style>
