<template>
  <div class="avatar position-relative">
    <img
      :id="`student-avatar-${student.uid}-img`"
      :alt="ariaLabel"
      :aria-label="ariaLabel"
      class="avatar-img"
      :class="`student-avatar-${size} ${currentUser.inDemoMode ? 'img-blur' : ''}`"
      :src="avatarUrl"
      :style="{backgroundImage: `url(${avatarUrl})`, backgroundRepeat: 'repeat'}"
      @error="avatarError"
    />
    <PillCount
      v-if="alertCount"
      :id="`student-avatar-${student.uid}-alert-count`"
      :aria-label="pluralize('alert', alertCount)"
      class="student-avatar-alert-count"
      color="warning"
    >
      {{ alertCount }}
      <v-tooltip
        :id="`student-avatar-${student.uid}-tooltip`"
        activator="parent"
        aria-hidden="true"
        location="bottom"
        :text="pluralize('alert', alertCount)"
      />
    </PillCount>
  </div>
</template>

<script setup>
import avatarPlaceholder from '@/assets/avatar-50.png'
import PillCount from '@/components/util/PillCount'
import {isNil} from 'lodash'
import {pluralize} from '@/lib/utils'
import {onMounted, ref} from 'vue'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  alertCount: {
    default: undefined,
    required: false,
    type: Number
  },
  size: {
    required: true,
    type: String,
    validator: v => ['small', 'medium', 'large'].indexOf(v) > -1
  },
  student: {
    required: true,
    type: Object
  }
})

const ariaLabel = ref(`Photo of ${props.student.firstName} ${props.student.lastName}`)
const avatarUrl = ref(props.student.photoUrl)
const currentUser = useContextStore().currentUser

onMounted(() => {
  if (!isNil(props.alertCount)) {
    ariaLabel.value += props.alertCount === 1 ? ' (one alert)' : ` (${props.alertCount} alerts)`
  }
})

const avatarError = () => {
  avatarUrl.value = avatarPlaceholder
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
