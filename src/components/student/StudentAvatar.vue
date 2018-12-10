<template>
  <div :class="{'student-avatar-large-container': size === 'large'}">
    <img class="avatar"
         :class="{'student-avatar-large': size === 'large', 'student-avatar-small': size === 'small', 'img-blur': inDemoMode}"
         :aria-label="'Photo of ' + student.firstName + ' ' + student.lastName"
         tabindex="0"
         :src="baseUrl + '/api/student/' + student.uid + '/photo'"
         @error="`${baseUrl}/static/app/shared/avatar-50.png`"/>
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
import AppConfig from '@/mixins/AppConfig';
import UserMetadata from '@/mixins/UserMetadata';

export default {
  name: 'StudentAvatar',
  mixins: [AppConfig, UserMetadata],
  props: {
    size: String,
    student: Object,
    alertCount: Number
  },
  computed: {
    avatarFallback: () => this.apiBaseUrl + '/static/app/shared/avatar-50.png'
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
  align-items: center;
  display: flex;
  flex: 0 0 60px;
}

.student-avatar-large {
  border-radius: 50px;
  height: 100px;
  width: 100px;
}

.student-avatar-large-container {
  margin: 20px;
  position: relative;
}

.student-avatar-small {
  border: 1px;
  border-radius: 15px;
  height: 30px;
  padding: 2px 0 2px 0;
  width: 30px;
}
</style>
