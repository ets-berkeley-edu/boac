<template>
  <div class="position-relative">
    <img
      :class="avatarStyle"
      :aria-label="ariaLabel"
      :alt="ariaLabel"
      :src="avatarUrl"
      class="avatar"
      @error="avatarError"
    />
    <div
      v-if="alertCount"
      aria-hidden="true"
      class="student-avatar-alert-count"
    >
      <span
        v-b-tooltip.hover.bottom
        :title="`${alertCount} alert${alertCount === 1 ? '' : 's'}`"
      >
        {{ alertCount }}
      </span>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'

export default {
  name: 'StudentAvatar',
  mixins: [Context, Util],
  props: {
    size: {
      required: true,
      type: String,
      validator: v => ['small', 'medium', 'large'].indexOf(v) > -1
    },
    student: {
      required: true,
      type: Object
    },
    alertCount: {
      default: undefined,
      required: false,
      type: Number
    }
  },
  data: () => ({
    ariaLabel: undefined,
    avatarStyle: undefined,
    avatarUrl: undefined
  }),
  created() {
    this.ariaLabel = `Photo of ${this.student.firstName} ${this.student.lastName}`
    if (!this._isNil(this.alertCount)) {
      this.ariaLabel += this.alertCount === 1 ? ' (one alert)' : ` (${this.alertCount} alerts)`
    }
    this.avatarUrl = this.student.photoUrl
    this.avatarStyle = `student-avatar-${this.size} ${
      this.currentUser.inDemoMode ? 'img-blur' : ''
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
