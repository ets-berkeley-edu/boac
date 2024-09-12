<template>
  <div class="align-center d-flex flex-nowrap justify-space-between my-2 w-100">
    <div
      class="font-size-16 header-text ml-3 text-white"
    >
      <span class="hide-in-narrow-viewport">
        <span v-if="startsWith($route.path, '/home')" class="text-no-wrap">
          <span class="font-weight-bold">UC Berkeley</span>
          Online Advising
        </span>
        <router-link
          v-if="!startsWith($route.path, '/home')"
          id="home-header"
          class="text-no-wrap"
          to="/"
        >
          <span class="font-weight-bold">UC Berkeley</span>
          Online Advising
        </router-link>
      </span>
      <router-link id="home-header" class="show-in-narrow-viewport" to="/">
        <v-icon :icon="mdiHome" />
      </router-link>
    </div>
    <AdvancedSearch class="ml-3" />
    <HeaderMenu class="mx-3" />
  </div>
</template>

<script setup lang="ts">
import AdvancedSearch from '@/components/search/AdvancedSearch.vue'
import HeaderMenu from '@/components/header/HeaderMenu.vue'
import {mdiHome} from '@mdi/js'
import {startsWith} from 'lodash'
</script>

<style scoped>
/* eslint-disable vue-scoped-css/no-unused-selector */
.header-text a:link,
.header-text a:visited {
/* eslint-enable vue-scoped-css/no-unused-selector */
  border: 0;
  color: white;
  cursor: pointer;
  -moz-outline-style: none;
  outline-style: none;
  text-decoration: none;
}
/* eslint-disable vue-scoped-css/no-unused-selector */
.header-text a:hover,
.header-text a:focus,
.header-text a:active {
/* eslint-enable vue-scoped-css/no-unused-selector */
  color: #ddd !important;
}
@media (max-width: 600px) {
  .hide-in-narrow-viewport {
    display: none;
  }
}
@media (min-width: 600px) {
  .show-in-narrow-viewport {
    display: none;
  }
}
</style>
