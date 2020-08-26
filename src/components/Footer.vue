<template>
  <b-container fluid class="w-auto p-0">
    <b-row class="w-100">
      <b-col sm="7" class="mb-3 mr-auto">
        <img alt="UC Berkeley logo" src="@/assets/uc-berkeley-logo.svg" />
      </b-col>
      <b-col sm="5" class="pr-0">
        <div>
          Problem? Question? Suggestion?
          Email <a :href="`mailto:${$config.supportEmailAddress}`" target="_blank">{{ $config.supportEmailAddress }}<span class="sr-only"> (new browser tab will open)</span></a>
        </div>
        &copy; 2020 The Regents of the University of California
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import Context from '@/mixins/Context'

export default {
  name: 'Footer',
  mixins: [Context]
}
</script>
