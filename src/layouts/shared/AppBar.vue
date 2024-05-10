<template>
  <div class="align-center d-flex flex-nowrap justify-space-between my-2 w-100">
    <div
      class="font-size-16 header-text ml-3 text-white"
      role="banner"
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
        <v-icon :icon="mdiHome" color="white" />
      </router-link>
    </div>
    <div class="ml-3">
      <AdvancedSearch />
    </div>
    <div class="mx-3">
      <HeaderMenu />
    </div>
  </div>
</template>

<script setup lang="ts">
import AdvancedSearch from '@/components/search/AdvancedSearch'
import HeaderMenu from '@/components/header/HeaderMenu'
import {mdiHome} from '@mdi/js'
import {startsWith} from 'lodash'

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
