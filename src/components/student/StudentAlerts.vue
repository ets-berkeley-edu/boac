<template>
  <div>
    <div v-if="alerts.shown.length">
      <div v-for="alert in alerts.shown"
           :key="alert.id"
           :id="'alert-' + alert.id"
           class="alert alert-warning student-alert">
        <div class="student-alert-item">
          <StudentAlertMessage :alert="alert"></StudentAlertMessage>
          <button :id="'dismiss-alert-' + alert.id"
                  class="btn btn-link btn-link-close"
                  @click="dismissAlert(alert.id)"
                  title="Dismiss alert"
                  aria-label="Close">&times;</button>
        </div>
      </div>
    </div>
    <div v-if="!showDismissedAlerts && alerts.dismissed.length">
      <button class="btn btn-link toggle-btn-link"
               @click="showDismissedAlerts=true">
        View dismissed status alerts
      </button>
    </div>
    <div v-if="showDismissedAlerts && alerts.dismissed.length">
      <button class="btn btn-link toggle-btn-link"
              @click="showDismissedAlerts=false">
        Hide dismissed status alerts
      </button>
      <div class="alert alert-warning student-hold-notification">
        <div v-for="alert in alerts.dismissed" :key="alert.id" class="student-alert-item">
          <StudentAlertMessage :alert="alert"></StudentAlertMessage>
        </div>
      </div>
    </div>
    <div v-for="(hold, holdIndex) in student.holds"
         :key="holdIndex"
         :id="'hold-notification-' + holdIndex"
         class="alert alert-info student-hold-notification">
      Hold: {{ get(hold, 'reason.description') }}. {{ get(hold, 'reason.formalDescription') }}
    </div>
    <div v-if="student.sisProfile.withdrawalCancel">
      <span class="red-flag-small">
        {{ student.sisProfile.withdrawalCancel.description }}
        ({{ student.sisProfile.withdrawalCancel.reason }})
        {{ student.sisProfile.withdrawalCancel.date | date }}
      </span>
    </div>
  </div>
</template>

<script>
import _ from 'lodash';

import { dismissStudentAlert, getStudentAlerts } from '@/api/student';
import StudentAlertMessage from '@/components/student/StudentAlertMessage';
import Util from '@/mixins/Util';

export default {
  name: 'StudentAlerts',
  components: {
    StudentAlertMessage
  },
  data: () => ({
    alerts: {
      dismissed: [],
      shown: []
    },
    showDismissedAlerts: false
  }),
  mixins: [Util],
  props: {
    student: Object
  },
  created() {
    this.loadAlerts();
  },
  methods: {
    dismissAlert(alertId) {
      dismissStudentAlert(alertId).then(() => {
        var dismissed = _.remove(this.alerts.shown, { id: alertId });
        dismissed.forEach(d => this.alerts.dismissed.push(d));
      });
    },
    loadAlerts() {
      getStudentAlerts(this.student.sid).then(data => {
        this.alerts = data;
      });
    }
  }
};
</script>

<style>
.student-alert {
  margin: 10px 0;
  padding: 5px 15px;
  background-color: #fcf8e3;
}

.student-alert-item {
  padding: 5px 0;
}

.student-hold-notification {
  margin: 10px 0;
  padding: 5px 15px;
  background-color: #fff6ff;
  border-color: #f6e6f6;
  color: #745074;
}
</style>
