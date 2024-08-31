<template>
  <div>
    <a
      id="skip-to-content-link"
      class="sr-only"
      href="#content"
    >
      Skip to main content
    </a>
    <div
      class="font-size-16 header-text text-white"
      role="banner"
    >
      <div v-if="startsWith(route.path, '/home')" class="text-no-wrap">
        <span class="font-weight-bold">UC Berkeley</span>
        Online Advising
      </div>
      <router-link
        v-if="!startsWith(route.path, '/home')"
        id="home-header"
        class="text-no-wrap"
        to="/"
      >
        <span class="font-weight-bold">UC Berkeley</span>
        Online Advising
      </router-link>
    </div>
  </div>
</template>

<script setup>
import {startsWith} from 'lodash'
import {useRoute} from 'vue-router'

const route = useRoute()
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
