<template>
  <div id="student-status-degree-progress">
    <h3>Degree Progress</h3>
    <div v-if="!student.sisProfile.degreeProgress">
      No data
    </div>
    <table v-if="student.sisProfile.degreeProgress">
      <tr>
        <th>University Requirements</th>
        <th>Status</th>
      </tr>
      <tr v-for="requirement in student.sisProfile.degreeProgress.requirements"
          :key="requirement.name">
        <td>{{ requirement.name }}</td>
        <td>
          <i :class="{
                  'fas fa-check': requirement.status === 'Satisfied',
                  'fas fa-exclamation-triangle': requirement.status === 'Not Satisfied',
                  'fas fa-clock-o': requirement.status === 'In Progress'
              }"></i>
          {{ requirement.status }}
        </td>
      </tr>
    </table>
    <div v-if="student.sisProfile.degreeProgress">
      <div>Degree Progress as of {{student.sisProfile.degreeProgress.reportDate}}.</div>
      <div>
        Advisors can refresh this data at
        <a id="calcentral-student-profile-link"
           :href="student.studentProfileLink"
           aria-label="Open CalCentral in new window"
           target="_blank">CalCentral</a>.
      </div>
    </div>
    <StudentAlerts :student="student"/>
  </div>
</template>

<script>
import StudentAlerts from '@/components/student/StudentAlerts';
import Util from '@/mixins/Util';

export default {
  name: 'AcademicTimeline',
  mixins: [Util],
  components: {
    StudentAlerts
  },
  props: {
    student: Object
  }
};
</script>
