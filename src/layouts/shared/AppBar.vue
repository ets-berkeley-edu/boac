<template>
  <div class="align-center d-flex flex-nowrap justify-space-between my-2 w-100">
    <div class="font-size-16 header-text px-3">
      <NavLink
        id="home-header"
        class="text-no-wrap text-white"
        path="/home"
        aria-label="UC Berkeley Online Advising home page"
      >
        <span class="hide-in-narrow-viewport">
          <span class="font-weight-bold">UC Berkeley</span>
          Online Advising <span class="sr-only">&nbsp;home page</span>
        </span>
        <v-icon
          aria-hidden="true"
          class="show-in-narrow-viewport"
          :icon="mdiHome"
        />
      </NavLink>
    </div>
    <AdvancedSearch class="mx-3" />
    <HeaderMenu class="mr-4" />
  </div>
</template>

<script setup lang="ts">
import {mdiHome} from '@mdi/js'
import AdvancedSearch from '@/components/search/AdvancedSearch.vue'
import HeaderMenu from '@/components/header/HeaderMenu.vue'
import NavLink from '@/components/util/NavLink.vue'
</script>

<style scoped>
/* eslint-disable vue-scoped-css/no-unused-selector */
.header-text a:link, .header-text a:visited {
/* eslint-enable vue-scoped-css/no-unused-selector */
  border: 0;
  color: white;
  cursor: pointer;
  text-decoration: none;
}
/* eslint-disable vue-scoped-css/no-unused-selector */
.header-text a:hover, .header-text a:focus, .header-text a:active {
/* eslint-enable vue-scoped-css/no-unused-selector */
  opacity: var(--v-high-emphasis-opacity )
}
@media (max-width: 900px) {
  .hide-in-narrow-viewport {
    display: none;
  }
}
@media (min-width: 900px) {
  .show-in-narrow-viewport {
    display: none;
  }
}
</style>
