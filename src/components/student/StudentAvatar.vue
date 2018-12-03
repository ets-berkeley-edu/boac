<template>
  <div>
    <img class="student-avatar student-avatar-small"
         :aria-label="'Photo of ' + student.firstName + ' ' + student.lastName"
         tabindex="0"
         v-bind:class="{'img-blur': inDemoMode}"
         :src="baseUrl + '/api/student/' + student.uid + '/photo'"
         @error="avatarFallback"/>
  </div>
</template>

<script>
import store from '@/store';

export default {
  name: 'StudentAvatar',
  props: ['student'],
  computed: {
    inDemoMode: () => store.getters.user.inDemoMode,
    baseUrl: () => store.state.apiBaseUrl,
    avatarFallback: () =>
      store.state.apiBaseUrl + '/static/app/shared/avatar-50.png'
  }
};
</script>
