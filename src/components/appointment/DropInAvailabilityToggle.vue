<template>
  <div>
    <div class="d-flex mb-2">
      <div v-if="!$currentUser.isAdmin" class="availability-status-outer flex-row">
        <b-form-group>
          <b-form-radio-group
            :id="toggleElementId"
            v-model="selectedStatus"
            class="drop-in-status-toggle"
            :options="dropInStatusOptions"
            buttons
            name="drop-in-status-toggle"
            size="sm"
            @change="changeStatus"
          ></b-form-radio-group>
        </b-form-group>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import Util from '@/mixins/Util';
import { setDropInStatus } from '@/api/user';

export default {
  name: 'DropInAvailabilityToggle',
  mixins: [Context, Util],
  props: {
    deptCode: {
      type: String,
      required: true
    },
    isHomepage: {
      type: Boolean,
      required: true
    },
    status: {
      type: String,
      required: true
    },
    uid: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      dropInStatusOptions: [
        { text: 'Off Duty', value: 'off_duty_waitlist'},
        { text: 'On Duty Drop-in Advisor', value: 'on_duty_advisor' },
        { text: 'On Duty Supervisor On Call', value: 'on_duty_supervisor' }
      ],
      isToggling: undefined,
      selectedStatus: this.status
    }
  },
  computed: {
    toggleElementId() {
      return `toggle-drop-in-status-${this.uid === this.$currentUser.uid ? 'me' : this.uid}`;
    }
  },
  created() {
    this.$eventHub.$on('drop-in-status-change', status => {
      this.selectedStatus = status;
    });
  },
  methods: {
    changeStatus: function(selected) {
      setDropInStatus(this.deptCode, this.uid, selected).then(() => {
        this.alertScreenReader(`Switching drop-in availability to ${this.status}`);
      });
    }
  }
};
</script>

<style scoped>
.availability-status-outer {
  align-items: center;
}
</style>

<style>
.drop-in-status-toggle .btn {
  background-color: #3b7ea5 !important;
  border-radius: 0 !important;
  border-width: 0 !important;
  margin-right: 5px !important;
}

.drop-in-status-toggle .btn:hover,
.drop-in-status-toggle .btn.active {
  background-color: #4a90e2 !important;
}
</style>
