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
    baseUrl: () => store.state.apiBaseUrl
  },
  methods: {
    avatarFallback: () => this.baseUrl + '/static/app/shared/avatar-50.png'
  }
};
</script>

<style scoped>
.student-avatar {
  background-image: url(/static/app/shared/avatar-50.png);
  background-size: cover;
  border: 5px solid #ccc;
  border-radius: 30px;
  height: 60px;
  object-fit: cover;
  width: 60px;
}
.student-avatar-small {
  border: 1px;
  border-radius: 15px;
  height: 30px;
  padding: 2px 0 2px 0;
  width: 30px;
}
</style>
