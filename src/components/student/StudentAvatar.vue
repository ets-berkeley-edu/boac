<template>
  <div>
    <img class="avatar"
         :class="{'avatar-large': size === 'large', 'avatar-small': size === 'small', 'img-blur': user.inDemoMode}"
         :aria-label="'Photo of ' + student.firstName + ' ' + student.lastName"
         tabindex="0"
         :src="baseUrl + '/api/student/' + student.uid + '/photo'"
         @error="avatarFallback"/>
  </div>
</template>

<script>
import store from '@/store';
import UserMetadata from '@/mixins/UserMetadata';

export default {
  name: 'StudentAvatar',
  mixins: [UserMetadata],
  props: ['size', 'student'],
  computed: {
    baseUrl: () => store.state.apiBaseUrl,
    avatarFallback: () =>
      store.state.apiBaseUrl + '/static/app/shared/avatar-50.png'
  }
};
</script>
