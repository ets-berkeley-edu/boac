<template>
  <div class="align-center container d-flex flex-row ml-2 mr-3">
    <div>
      <img
        id="avatar-verify-blur"
        alt="Picture of woman demonstrates blur effect when BOA demo mode is on."
        class="avatar student-avatar-large"
        :class="{'img-blur': currentUser.inDemoMode}"
        :src="blurAvatarUrl"
      />
    </div>
    <div class="ml-4">
      <div v-if="!isNil(currentUser.inDemoMode)">
        <div class="align-center widget-container d-flex">
          <div class="checkbox-container" :class="{'pt-1': isToggling}">
            <input
              v-if="!isToggling"
              id="toggle-demo-mode"
              v-model="inDemoMode"
              :aria-label="`Demo mode is ${inDemoMode ? 'On' : 'Off'}`"
              class="checkbox"
              :disabled="isToggling"
              type="checkbox"
              @change="toggle"
            />
            <v-progress-circular
              v-if="isToggling"
              id="toggle-demo-mode"
              color="primary"
              indeterminate
              size="22"
              width="3"
            />
          </div>
          <label for="toggling-demo-mode">
            {{ isToggling ? 'Toggling demo mode...' : `${inDemoMode ? 'On' : 'Off'}` }}
          </label>
        </div>
      </div>
      <div class="ml-1 text-medium-emphasis">
        In demo mode, student profile pictures and sensitive data will be blurred.
      </div>
    </div>
  </div>
</template>

<script setup>
import sampleBlurAvatar from '@/assets/sampleBlurAvatar.jpg'
import {alertScreenReader} from '@/lib/utils'
import {ref} from 'vue'
import {setDemoMode} from '@/api/user'
import {useContextStore} from '@/stores/context'
import {isNil} from 'lodash'

const blurAvatarUrl = sampleBlurAvatar
const currentUser = useContextStore().currentUser
const inDemoMode = ref(currentUser.inDemoMode)
const isToggling = ref(false)

const toggle = () => {
  isToggling.value = true
  alertScreenReader(`Switching demo mode ${inDemoMode.value ? 'on' : 'off' }`)
  setDemoMode(inDemoMode.value).then(() => {
    isToggling.value = false
  })
}
</script>

<style scoped>
#avatar-verify-blur {
  height: 50px;
  width: auto;
  border-radius: 50%;
}
.container {
  height: 80px;
  min-height: 80px;
}
.img-blur {
  filter: blur(20px);
}
.widget-container {
  height: 40px;
  min-height: 40px;
}
</style>
