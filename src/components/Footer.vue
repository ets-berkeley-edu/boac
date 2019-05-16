<template>
  <b-container fluid class="mb-2 mt-2">
    <b-row>
      <b-col sm="6" class="mb-2">
        <img src="@/assets/uc-berkeley-logo.svg" />
      </b-col>
      <b-col sm="6">
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
