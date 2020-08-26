<template>
  <div>
    <div class="d-flex flex-row mb-2 mr-3 mt-3 pb-4">
      <div class="ml-2 mr-2">
        <img
          id="avatar-verify-blur"
          :class="{'img-blur': $currentUser.inDemoMode}"
          :src="blurAvatarUrl"
          alt="Picture of woman demonstrates blur effect when BOA demo mode is on."
          class="avatar student-avatar-large" />
      </div>
      <div class="pl-2 pt-2">
        <div v-if="!isNil($currentUser.inDemoMode)">
          <b-form-checkbox
            v-if="!isToggling"
            id="toggle-demo-mode"
            v-model="inDemoMode"
            :disabled="isToggling"
            @change="toggle">
            <span class="sr-only">Demo mode is </span>{{ inDemoMode ? 'On' : 'Off' }}
          </b-form-checkbox>
          <div v-if="isToggling" class="demo-mode-label">
            <font-awesome icon="spinner" spin />
            Toggling demo mode...
          </div>
        </div>
        <div class="faint-text pt-2">
          In demo mode, student profile pictures and sensitive data will be blurred.
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import { setDemoMode } from '@/api/user'

export default {
  name: 'DemoModeToggle',
  mixins: [Context, Util],
  data: () => ({
    blurAvatarUrl: require('@/assets/sampleBlurAvatar.jpg'),
    inDemoMode: undefined,
    isToggling: undefined
  }),
  created() {
    this.inDemoMode = this.$currentUser.inDemoMode
  },
  methods: {
    toggle: function() {
      this.isToggling = true
      setDemoMode(!this.inDemoMode).then(() => {
        this.inDemoMode = !this.inDemoMode
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
</style>
