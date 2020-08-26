<template>
  <div>
    <div class="d-flex">
      <div v-if="!isNil(isEnabled)" class="advising-status-outer flex-row">
        <div
          :class="isEnabled ? 'advising-status-disabled' : 'advising-status-enabled'"
          class="aria-hidden advising-status">
          NO
        </div>
        <div class="toggle-btn-column">
          <button
            v-if="!isToggling"
            :id="buttonElementId"
            type="button"
            class="btn btn-link pt-0 pb-0 pl-1 pr-1"
            @click="toggle"
            @keyup.down="toggle">
            <span class="status-toggle-label">
              <font-awesome v-if="isEnabled" icon="toggle-on" class="toggle toggle-on"></font-awesome>
              <font-awesome v-if="!isEnabled" icon="toggle-off" class="toggle toggle-off"></font-awesome>
              <span class="sr-only">{{ isEnabled ? 'YES' : 'NO' }}</span>
            </span>
          </button>
          <div v-if="isToggling" class="pl-2">
            <font-awesome icon="spinner" spin />
          </div>
        </div>
        <div
          :class="isEnabled ? 'advising-status-enabled' : 'advising-status-disabled'"
          class="aria-hidden advising-status">
          YES
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import { disableDropInAdvising, enableDropInAdvising } from '@/api/user'

export default {
  name: 'DropInAdvisingToggle',
  mixins: [Context, Util],
  props: {
    deptCode: {
      type: String,
      required: true
    }
  },
  data: () => ({
    isEnabled: undefined,
    isToggling: undefined
  }),
  computed: {
    buttonElementId() {
      return `toggle-drop-in-advising-${this.deptCode}`
    }
  },
  created() {
    this.isEnabled = !!this.dropInStatus()
  },
  methods: {
    dropInStatus: function() {
      return this.find(this.$currentUser.dropInAdvisorStatus, ['deptCode', this.deptCode])
    },
    toggle: function() {
      this.isToggling = true
      const toggleDropInAdvising = this.isEnabled ? disableDropInAdvising : enableDropInAdvising
      toggleDropInAdvising(this.deptCode).then(() => {
        this.isEnabled = !!this.dropInStatus()
        this.isToggling = false
        this.alertScreenReader(`Switching drop-in advising ${this.isEnabled ? 'off' : 'on' }`)
        this.putFocusNextTick(this.buttonElementId)
      })
    }
  }
}
</script>

<style scoped>
.advising-status {
  font-size: 12px;
  text-transform: uppercase;
}
.advising-status-enabled {
  font-weight: 600;
}
.advising-status-disabled {
  color: #999999;
}
.advising-status-outer {
  align-items: center;
}
.toggle {
 font-size: 20px;
}
.toggle-btn-column {
  min-height: 28px;
  min-width: 36px;
}
.toggle-off {
   color: #999999;
}
.toggle-on {
   color: #00c13a;
}
</style>
