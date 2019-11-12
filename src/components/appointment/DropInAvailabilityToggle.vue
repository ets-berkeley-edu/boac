<template>
  <div>
    <div class="d-flex mb-2">
      <div v-if="!isNil(isAvailable)" class="availability-status-outer flex-row">
        <div v-if="!advisor" class="mr-2 availability-status">
          My availability status:
        </div>
        <div
          v-if="!isAvailable || !user.isAdmin"
          :class="isAvailable ? 'availability-status-disabled' : 'availability-status-active'"
          class="aria-hidden availability-status">
          Off duty
        </div>
        <div v-if="!user.isAdmin" class="toggle-btn-column">
          <button
            :id="`toggle-drop-in-availability-${uid}`"
            v-if="!isToggling"
            v-model="isAvailable"
            @click="toggle"
            @keyup="toggle"
            type="button"
            class="btn btn-link pt-0 pb-0 pl-1 pr-1">
            <span class="status-toggle-label">
              <font-awesome v-if="isAvailable" icon="toggle-on" class="toggle toggle-on"></font-awesome>
              <font-awesome v-if="!isAvailable" icon="toggle-off" class="toggle toggle-off"></font-awesome>
              <span class="sr-only">{{ isAvailable ? 'On duty' : 'Off duty' }}</span>
            </span>
          </button>
          <div v-if="isToggling" class="pl-2">
            <font-awesome icon="spinner" spin />
          </div>
        </div>
        <div
          v-if="isAvailable || !user.isAdmin"
          :class="isAvailable ? 'availability-status-active' : 'availability-status-disabled'"
          class="aria-hidden availability-status">
          On duty
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { setDropInAvailability } from '@/api/user';

export default {
  name: 'DropInAvailabilityToggle',
  mixins: [Context, UserMetadata, Util],
  props: {
    advisor: {
      type: Object,
      required: false
    },
    deptCode: {
      type: String,
      required: true
    }
  },
  data: () => ({
    isToggling: undefined,
    uid: undefined
  }),
  computed: {
    isAvailable: {
      get: function() {
        if (this.advisor) {
          return this.advisor.available;
        } else {
          const dropInAdvisorStatus = this.find(this.user.dropInAdvisorStatus, {'deptCode': this.deptCode.toUpperCase()});
          if (dropInAdvisorStatus) {
            return dropInAdvisorStatus.available;
          } else {
            return null;
          }
        }
      },
      set: function(newValue) {
        if (this.advisor) {
          this.advisor.available = newValue;
        }
      }
    }
  },
  created() {
    this.uid = this.advisor ? this.advisor.uid : 'me';
  },
  methods: {
    toggle: function() {
      this.isToggling = true;
      setDropInAvailability(this.deptCode, this.uid, !this.isAvailable).then(() => {
        this.isAvailable = !this.isAvailable;
        this.isToggling = false;
        this.alertScreenReader(`Switching drop-in availability ${this.isAvailable ? 'off' : 'on' }`);
      });
    }
  }
};
</script>

<style scoped>
.availability-status {
  font-size: 12px;
  text-transform: uppercase;
}
.availability-status-active {
  font-weight: 600;
}
.availability-status-disabled {
  color: #999999;
}
.availability-status-outer {
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
