<template>
  <div id="app" class="fill-viewport">
    <VueAnnouncer />
    <router-view></router-view>
    <DismissibleFooterAlert />
  </div>
</template>

<script>
import DismissibleFooterAlert from '@/components/util/DismissibleFooterAlert'

export default {
  name: 'App',
  components: {DismissibleFooterAlert}
}
</script>

<style>
@import './assets/styles/autocomplete-overrides.css';
@import './assets/styles/boac-global.css';
@import './assets/styles/bootstrap-overrides.css';
</style>
