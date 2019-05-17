<template>
  <b-container fluid class="w-auto p-0">
    <b-row class="w-100">
      <b-col sm="7" class="mb-3 mr-auto">
        <img src="@/assets/uc-berkeley-logo.svg" />
      </b-col>
      <b-col sm="5" class="pr-0">
        <div>
          Problem? Question? Suggestion? Email <a :href="`mailto:${supportEmailAddress}`" target="_blank">{{ supportEmailAddress }}</a>
        </div>
        &copy; 2019 The Regents of the University of California
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import Context from '@/mixins/Context';

export default {
  name: 'Footer',
  mixins: [Context]
};
</script>
