<template>
  <b-container fluid class="mt-2 mb-3">
    <b-row>
      <b-col cols="auto" class="mr-auto pb-1">
        <img src="@/assets/uc-berkeley-logo.svg" />
      </b-col>
      <b-col cols="auto">
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
