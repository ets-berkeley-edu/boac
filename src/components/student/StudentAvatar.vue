<template>
  <div class="position-relative">
    <img
      :class="avatarStyle"
      :aria-label="`Photo of ${student.firstName} ${student.lastName}`"
      :alt="`Photo of ${student.firstName} ${student.lastName}`"
      :src="avatarUrl"
      class="avatar"
      tabindex="0"
      @error="avatarError" />
    <div
      v-if="alertCount"
      class="inactive-info-icon student-avatar-alert-count">
      <span
        v-b-tooltip.hover.bottom
        :title="`${alertCount} alert${alertCount === 1 ? '' : 's'}`">
        {{ alertCount }}
      </span>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'

export default {
  name: 'StudentAvatar',
  mixins: [Context],
  props: {
    size: String,
    student: Object,
    alertCount: Number
  },
  data: () => ({
    avatarStyle: undefined,
    avatarUrl: undefined
  }),
  created() {
    this.avatarUrl = this.student.photoUrl
    this.avatarStyle = `student-avatar-${this.size} ${
      this.$currentUser.inDemoMode ? 'img-blur' : ''
    }`
  },
  methods: {
    avatarError() {
      this.avatarUrl = require('@/assets/avatar-50.png')
    }
  }
}
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
.student-avatar-large {
  border-radius: 75px;
  height: 150px;
  width: 150px;
}
.student-avatar-medium {
  border-radius: 50px;
  height: 100px;
  width: 100px;
}
.student-avatar-small {
  border: 1px;
  border-radius: 15px;
  height: 30px;
  padding: 2px 0 2px 0;
  width: 30px;
}
</style>
