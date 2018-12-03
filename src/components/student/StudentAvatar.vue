<template>
  <div>
    <img class="avatar"
         :class="{'avatar-large': size === 'large', 'avatar-small': size === 'small'}"
         :aria-label="'Photo of ' + student.firstName + ' ' + student.lastName"
         tabindex="0"
         :src="baseUrl + '/api/student/' + student.uid + '/photo'"
         @error="avatarFallback"/>
  </div>
</template>

<script>
import store from '@/store';

export default {
  name: 'StudentAvatar',
  props: ['size', 'student'],
  computed: {
    inDemoMode: () => store.getters.user.inDemoMode,
    baseUrl: () => store.state.apiBaseUrl,
    avatarFallback: () =>
      store.state.apiBaseUrl + '/static/app/shared/avatar-50.png'
  }
};
</script>
