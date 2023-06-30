<template>
  <div>
    <a
      id="skip-to-content-link"
      href="#content"
      class="sr-only"
    >
      Skip to main content
    </a>
    <div
      class="font-size-16 header-text text-white"
      role="banner"
    >
      <div v-if="$_.startsWith($route.path, '/home')" class="text-nowrap">
        <span class="font-weight-bolder">UC Berkeley</span>
        Online Advising
      </div>
      <router-link
        v-if="!$_.startsWith($route.path, '/home')"
        id="home-header"
        class="text-nowrap"
        to="/"
      >
        <span class="font-weight-bolder">UC Berkeley</span>
        Online Advising
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HeaderBranding'
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
