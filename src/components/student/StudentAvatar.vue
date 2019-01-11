<template>
  <div class="student-avatar-container" :class="{'student-avatar-large-container': size === 'large-padded'}">
    <img class="avatar"
         :class="{
           'student-avatar-large': ['large', 'large-padded'].includes(size),
           'student-avatar-small': size === 'small',
           'img-blur': user.inDemoMode
         }"
         :aria-label="'Photo of ' + student.firstName + ' ' + student.lastName"
         tabindex="0"
         :src="avatarUrl"
         @error="avatarError"/>
    <div class="student-avatar-alert-count home-inactive-info-icon"
         v-if="alertCount">
      <span v-b-tooltip.hover.bottom
            :title="`${alertCount} alert${alertCount === 1 ? '' : 's'}`">
        {{ alertCount }}
      </span>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import UserMetadata from '@/mixins/UserMetadata';

export default {
  name: 'StudentAvatar',
  mixins: [Context, UserMetadata],
  data: () => ({
    avatarUrl: ''
  }),
  created() {
    this.avatarUrl =
      this.apiBaseUrl + '/api/student/' + this.student.uid + '/photo';
  },
  methods: {
    avatarError() {
      this.avatarUrl = require('@/assets/avatar-50.png');
    }
  },
  props: {
    size: String,
    student: Object,
    alertCount: Number
  }
};
</script>

<style scoped>
.avatar {
  background-image: url('~@/assets/avatar-50.png');
  background-size: cover;
  border: 5px solid #ccc;
  border-radius: 30px;
  height: 60px;
  object-fit: cover;
  width: 60px;
}

.student-avatar-alert-count {
  background-color: #f0ad4e;
  border-radius: 15px;
  border: 2px solid #fff;
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  object-fit: cover;
  padding-top: 2px;
  position: absolute;
  text-align: center;
  height: 30px;
  width: 30px;
  top: 5%;
  right: 5%;
}

.student-avatar-container {
  position: relative;
}

.student-avatar-large {
  border-radius: 50px;
  height: 100px;
  width: 100px;
}

.student-avatar-large-container {
  margin: 20px;
}

.student-avatar-small {
  border: 1px;
  border-radius: 15px;
  height: 30px;
  padding: 2px 0 2px 0;
  width: 30px;
}
</style>
