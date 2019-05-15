<template>
  <div class="d-flex w-100">
    <div class="ml-2">
      <img src="@/assets/uc-berkeley-logo.svg" />
    </div>
    <div class="ml-auto">
      <div>
        Problem? Question? Suggestion? Email <a :href="`mailto:${supportEmailAddress}`" target="_blank">{{ supportEmailAddress }}</a>
      </div>
      &copy; 2019 The Regents of the University of California
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';

export default {
  name: 'Footer',
  mixins: [Context]
};
</script>
