<template>
  <div>
    <div class="d-flex flex-row mb-2 mr-3 mt-3 pb-4">
      <div class="ml-2 mr-2">
        <img
          id="avatar-verify-blur"
          :class="{'img-blur': currentUser.inDemoMode}"
          :src="blurAvatarUrl"
          alt="Picture of woman demonstrates blur effect when BOA demo mode is on."
          class="avatar student-avatar-large"
        />
      </div>
      <div class="pl-3 ">
        <div v-if="!_isNil(currentUser.inDemoMode)">
          <v-checkbox
            v-if="!isToggling"
            id="toggle-demo-mode"
            v-model="inDemoMode"
            :disabled="isToggling"
            :label="`${inDemoMode ? 'On' : 'Off'}`"
            :aria-label="`Demo mode is ${inDemoMode ? 'On' : 'Off'}`"
            @change="toggle"
          >
          </v-checkbox>
          <div v-if="isToggling" class="demo-mode-label">
            <v-progress-circular size="small" />
            Toggling demo mode...
          </div>
        </div>
        <div class="faint-text"
             :class="{'text-description': !isToggling}"
        >
          In demo mode, student profile pictures and sensitive data will be blurred.
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import {setDemoMode} from '@/api/user'
import sampleBlurAvatar from '@/assets/sampleBlurAvatar.jpg'

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
        this.alertScreenReader(`Switching demo mode ${this.inDemoMode ? 'off' : 'on' }`)
      })
    }
  }
}
</script>

<style scoped>
.demo-mode-label {
  font-weight: 500;
  padding-bottom: 3px;
}

.img-blur {
  filter: blur(20px);
}

.text-description {
  position: relative;
  top: -20px;
  left: 10px;
}

#avatar-verify-blur {
  height: 50px;
  width: auto;
  border-radius: 50%;

}
</style>
