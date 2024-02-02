<template>
  <div id="app" class="font-size-14 vh-100">
    <div
      id="announcer"
      :aria-live="screenReaderAlert.politeness"
      class="sr-only"
    >
      {{ screenReaderAlert.message }}
    </div>
    <router-view></router-view>
    <DismissibleFooterAlert />
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import DismissibleFooterAlert from '@/components/util/DismissibleFooterAlert'

export default {
  name: 'App',
  components: {DismissibleFooterAlert},
  mixins: [Context]
}
</script>

<style>
@import './assets/styles/autocomplete-overrides.css';
@import './assets/styles/boac-global.css';
@import './assets/styles/bootstrap-overrides.css';
</style>
