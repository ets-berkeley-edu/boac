<template>
  <div class="avatar position-relative">
    <img
      :id="`student-avatar-${student.uid}-img`"
      :alt="ariaLabel"
      :aria-label="ariaLabel"
      class="avatar-img"
      :class="avatarStyle"
      :src="avatarUrl"
      :style="{backgroundImage: `url(${avatarUrl})`, backgroundRepeat: 'repeat'}"
      @error="avatarError"
    />
    <PillCount
      v-if="alertCount"
      :id="`student-avatar-${student.uid}-alert-count`"
      :aria-label="alertText"
      class="student-avatar-alert-count"
      color="warning"
    >
      {{ alertCount }}
      <v-tooltip
        :id="`student-avatar-${student.uid}-tooltip`"
        activator="parent"
        aria-hidden="true"
        location="bottom"
        :text="alertText"
      />
    </PillCount>
  </div>
</template>

<script setup>
import avatarPlaceholder from '@/assets/avatar-50.png'
import {isNil} from 'lodash'
import {pluralize} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
</script>

<script>
import PillCount from '@/components/util/PillCount'

export default {
  name: 'StudentAvatar',
  components: {PillCount},
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
  computed: {
    alertText() {
      return pluralize('alert', this.alertCount)
    }
  },
  created() {
    this.ariaLabel = `Photo of ${this.student.firstName} ${this.student.lastName}`
    if (!isNil(this.alertCount)) {
      this.ariaLabel += this.alertCount === 1 ? ' (one alert)' : ` (${this.alertCount} alerts)`
    }
    this.avatarUrl = this.student.photoUrl
    this.avatarStyle = `student-avatar-${this.size} ${
      useContextStore().currentUser.inDemoMode ? 'img-blur' : ''
    }`
  },
  methods: {
    avatarError() {
      this.avatarUrl = avatarPlaceholder
    }
  }
}
</script>

<style scoped>
.avatar-img {
  background-size: cover;
  border: 5px solid #ccc;
  border-radius: 30px;
  height: 60px;
  object-fit: cover;
  width: 60px;
}
.avatar .student-avatar-alert-count {
  display: block;
  border: 2px solid #fff;
  font-size: 14px !important;
  font-weight: 500;
  margin: 0px auto;
  object-fit: cover;
  padding: 2px !important;
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
