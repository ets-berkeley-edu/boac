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
      <div v-if="!_isNil(currentUser.inDemoMode)">
        <div class="align-center checkbox-container d-flex">
          <v-checkbox
            v-if="!isToggling"
            id="toggle-demo-mode"
            v-model="inDemoMode"
            :aria-label="`Demo mode is ${inDemoMode ? 'On' : 'Off'}`"
            color="primary"
            density="compact"
            :disabled="isToggling"
            hide-details
            :label="`${inDemoMode ? 'On' : 'Off'}`"
            @change="toggle"
          />
          <div v-if="isToggling" class="align-center d-flex font-weight-700 my-1">
            <v-progress-circular
              class="mr-1"
              color="grey"
              indeterminate
              size="25"
            />
            <span class="text-grey">
              Toggling demo mode...
            </span>
          </div>
        </div>
      </div>
      <div class="ml-1 text-grey">
        In demo mode, student profile pictures and sensitive data will be blurred.
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import sampleBlurAvatar from '@/assets/sampleBlurAvatar.jpg'
import Util from '@/mixins/Util'
import {alertScreenReader} from '@/lib/utils'
import {setDemoMode} from '@/api/user'

export default {
  name: 'DemoModeToggle',
  mixins: [Context, Util],
  data: () => ({
    blurAvatarUrl: sampleBlurAvatar,
    inDemoMode: undefined,
    isToggling: undefined
  }),
  created() {
    this.inDemoMode = this.currentUser.inDemoMode
  },
  methods: {
    toggle() {
      this.isToggling = true
      setDemoMode(this.inDemoMode).then(() => {
        this.isToggling = false
        alertScreenReader(`Switching demo mode ${this.inDemoMode ? 'off' : 'on' }`)
      })
    }
  }
}
</script>

<style scoped>
.checkbox-container {
  height: 40px;
  min-height: 40px;
}
.container {
  height: 80px;
  min-height: 80px;
}
.img-blur {
  filter: blur(20px);
}
#avatar-verify-blur {
  height: 50px;
  width: auto;
  border-radius: 50%;

}
</style>
