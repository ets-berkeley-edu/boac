<template>
  <div>
    <Spinner/>
    <div v-if="!loading">
      <div class="flex-row full-width" id="student-profile-container">
        <div class="student-profile-photo-container" id="student-profile-photo-container">
          <StudentAvatar :student="student" size="large"/>
        </div>
        <div class="student-profile-bio-container" id="student-profile-bio-container">
          <div class="student-bio-contact">
            <h1 class="student-section-header"
                id="student-name-header"
                :class="{'demo-mode-blur': inDemoMode}">
              {{student.name}}
            </h1>
            <h2 class="sr-only">Profile</h2>
            <div class="sr-only" v-if="student.sisProfile.preferredName !== student.name">Preferred name</div>
            <div class="student-preferred-name"
                 id="student-preferred-name"
                 :class="{'demo-mode-blur': inDemoMode}"
                 v-if="student.sisProfile.preferredName !== student.name">
              {{student.sisProfile.preferredName}}</div>
            <div class="student-bio-sid" id="student-bio-sid">
              SID <span :class="{'demo-mode-blur': inDemoMode}">{{student.sid}}</span>
            </div>
            <div>
              <i class="fas fa-envelope"></i>
              <span class="sr-only">Email</span>
              <a id="student-mailto"
                 :href="'mailto:' + student.sisProfile.emailAddress"
                 :class="{'demo-mode-blur': inDemoMode}">
                 {{student.sisProfile.emailAddress}}</a>
            </div>
            <div v-if="student.sisProfile.phoneNumber">
              <i class="fas fa-phone"></i>
              <span class="sr-only">Phone number</span>
              <span :class="{'demo-mode-blur': inDemoMode}"
                    id="student-phone-number"
                    tabindex="0">
                {{student.sisProfile.phoneNumber}}</span>
            </div>
          </div>
          <div id="student-bio-inactive" v-if="displayAsInactive(student)">
            <div class="student-bio-header student-bio-inactive">Inactive</div>
          </div>
          <div id="student-bio-athletics" v-if="student.athleticsProfile">
            <div v-for="membership in student.athleticsProfile.athletics" :key="membership.groupName">
              <div class="student-bio-header">{{membership.groupName}}</div>
            </div>
          </div>
          <div id="student-bio-majors">
            <h3 class="sr-only">Major</h3>
            <div v-for="plan in student.sisProfile.plans" :key="plan.description" class="student-bio-details-outer">
              <div class="student-bio-header">
                <span v-if="!plan.degreeProgramUrl">{{plan.description}}</span>
                <a v-if="plan.degreeProgramUrl"
                   :href="plan.degreeProgramUrl"
                   target="_blank"
                   :aria-label="'Open ' + plan.description + ' program page in new window'">
                   {{plan.description}}</a>
              </div>
              <div class="student-bio-details">
                <div v-if="plan.program">{{plan.program}}</div>
              </div>
            </div>
          </div>
          <div id="student-bio-level">
            <h3 class="sr-only">Level</h3>
            <div class="student-bio-header">{{student.sisProfile.level.description}}</div>
          </div>
          <div class="student-bio-details-outer">
            <div class="student-bio-details" id="student-bio-terms-in-attendance" v-if="student.sisProfile.termsInAttendance">
              {{ 'Term' | pluralize(student.sisProfile.termsInAttendance) }} in Attendance
            </div>
            <div class="student-bio-details"
                 id="student-bio-expected-graduation"
                 v-if="student.sisProfile.expectedGraduationTerm && student.sisProfile.level.code !== 'GR'">
              Expected graduation {{student.sisProfile.expectedGraduationTerm.name}}
            </div>
          </div>
          <div class="student-curated-groups-box" id="student-curated-groups-box">
            <div>
              <h3 class="student-bio-header">Curated Groups</h3>
            </div>
            <div class="curated-cohort-checkbox">
              <span class="faint-text">&quot;Pardon Our Progress&quot;</span>
            </div>
          </div>
        </div>
        <div class="student-profile-status-container" id="student-profile-status-container">
          <h2 class="sr-only">Academic Status</h2>
          <div class="flex-row student-status-box">
            <h3 class="sr-only">Units</h3>
            <div class="student-status-box-left" id="student-status-units-completed">
              <div class="student-status-legend">Units Completed</div>
              <div class="student-status-number" v-if="cumulativeUnits">{{cumulativeUnits}}</div>
              <div class="student-status-number" v-if="!cumulativeUnits">--<span class="sr-only">No data</span></div>
            </div>
            <div class="student-chart-outer" id="student-status-unit-totals">
              <div class="student-status-legend student-status-legend-heading" aria-hidden="true">Unit Totals</div>
              <div class="student-chart-units-container" id="student-chart-units-container" aria-hidden="true"
                   v-if="showUnitTotals">
                  &quot;Pardon Our Progress&quot;
              </div>
              <div class="student-status-legend student-status-legend-small"
                   v-if="!showUnitTotals">
                  Units Not Yet Available
              </div>
              <div class="sr-only" v-if="showUnitTotals" id="student-status-currently-enrolled-units">
                Currently enrolled units: {{currentEnrolledUnits || '0'}}
              </div>
            </div>
          </div>
          <div class="student-status-box">
            <h3 class="sr-only">GPA</h3>
            <div class="flex-row">
              <div class="student-status-box-left" id="student-status-cumulative-gpa">
                <div class="student-status-legend">Cumulative GPA</div>
                <div class="student-status-number">
                  {{student.sisProfile.cumulativeGPA || '--'}}
                </div>
                <div class="sr-only" v-if="!student.sisProfile.cumulativeGPA">No data</div>
              </div>
              <div class="student-chart-outer" id="student-status-gpa-trends">
                <div class="student-status-legend student-status-legend-heading">GPA Trends</div>
                <div class="student-status-legend student-status-legend-small">
                  &quot;Pardon Our Progress&quot;
                </div>
              </div>
            </div>
          </div>
          <div class="student-status-box student-status-box-degree-progress" id="student-status-degree-progress">
            <h3 class="student-progress-header">Degree Progress</h3>
            <div class="student-status-no-data" v-if="!student.sisProfile.degreeProgress">
              No data
            </div>
            <table class="student-status-table" v-if="student.sisProfile.degreeProgress">
              <tr>
                <th>University Requirements</th>
                <th>Status</th>
              </tr>
              <tr v-for="requirement in student.sisProfile.degreeProgress.requirements" :key="requirement.name">
                <td>{{requirement.name}}</td>
                <td>
                  <i :class="{
                          'fas fa-check student-bio-table-icon': requirement.status === 'Satisfied',
                          'fas fa-exclamation-triangle student-bio-table-icon': requirement.status === 'Not Satisfied',
                          'fas fa-clock-o student-bio-table-icon': requirement.status === 'In Progress'
                      }"></i>
                  {{requirement.status}}
                </td>
              </tr>
            </table>
            <div class="student-bio-subdetails" v-if="student.sisProfile.degreeProgress">
              <div>Degree Progress as of {{student.sisProfile.degreeProgress.reportDate}}.</div>
              <div>
                Advisors can refresh this data at
                <a :href="student.studentProfileLink" target="_blank" aria-label="Open CalCentral in new window">CalCentral</a>.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import _ from 'lodash';
import { getStudentDetails } from '@/api/student';
import Loading from '@/mixins/Loading.vue';
import Spinner from '@/components/Spinner.vue';
import StudentAvatar from '@/components/student/StudentAvatar';
import StudentMetadata from '@/mixins/StudentMetadata';
import store from '@/store';

export default {
  name: 'Student',
  mixins: [Loading, StudentMetadata],
  components: {
    Spinner,
    StudentAvatar
  },
  created() {
    this.inDemoMode = store.getters.user.inDemoMode;
    var uid = this.$route.path.split('_').pop();
    this.loadStudent(uid);
  },
  methods: {
    loadStudent(uid) {
      getStudentDetails(uid).then(data => {
        this.student = data;
        this.cumulativeUnits = _.get(
          this.student,
          'sisProfile.cumulativeUnits'
        );
        var termId = store.getters.config.currentEnrollmentTermId.toString();
        var currentEnrollmentTerm = _.find(
          _.get(this.student, 'enrollmentTerms'),
          {
            termId: termId
          }
        );
        if (currentEnrollmentTerm) {
          this.currentEnrolledUnits = _.get(
            currentEnrollmentTerm,
            'enrolledUnits'
          );
        }
        this.showUnitTotals = this.cumulativeUnits || this.currentEnrolledUnits;
        this.loaded();
      });
    }
  }
};
</script>

<style scoped>
.student-bio-contact {
  margin: 20px 0;
  flex: 1;
}
.student-bio-details {
  color: #999;
  font-size: 14px;
}
.student-bio-details-outer {
  margin-bottom: 10px;
}
.student-bio-header {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 5px 0;
}
.student-bio-inactive {
  color: #cf1715;
  text-transform: uppercase;
}
.student-bio-sid {
  font-size: 14px;
  font-weight: bold;
  margin: 5px 0;
}
.student-bio-subdetails {
  color: #999;
  font-size: 11px;
  font-style: italic;
  margin-top: 10px;
  text-align: center;
}
.student-chart-outer {
  border-left: 1px solid #999;
  flex: 1;
  margin: 0 10px;
  padding-left: 10px;
}
.student-chart-units-container {
  height: 60px;
  margin-top: 10px;
}
.student-curated-groups-box {
  background: #fff;
  border: solid 1px #999;
  border-radius: 3px;
  font-size: 20px;
  font-weight: 400;
  margin-right: 50px;
  padding: 15px 15px 15px 14px;
  text-align: left;
}
.student-preferred-name {
  font-size: 20px;
  font-weight: 400;
  margin: 0 0 10px 0;
}
.student-profile-bio-container {
  background: #e3f5ff;
  flex: 4;
}
.student-profile-photo-container {
  background: #e3f5ff;
  flex: 0;
}
.student-profile-status-container {
  background: #8bbdda;
  flex: 3;
}
.student-progress-header {
  font-size: 16px;
  font-weight: 600;
  margin-top: 10px;
  text-align: left;
}
.student-section-header {
  font-size: 24px;
  font-weight: bold;
}
.student-status-box {
  background: #fff;
  border: solid 1px #999;
  border-radius: 10px;
  font-size: 20px;
  font-weight: 400;
  margin: 15px 10px;
  padding: 10px 15px;
  text-align: center;
}
.student-status-box-degree-progress {
  text-align: left;
}
.student-status-box-left {
  display: flex;
  flex: 0 0 115px;
  flex-direction: column-reverse;
  justify-content: flex-end;
}
.student-status-legend {
  color: #999;
  font-size: 13px;
  font-weight: 300;
  text-transform: uppercase;
}
.student-status-legend-heading {
  color: #000;
  font-weight: 600;
  padding-left: 5px;
  text-align: left;
}
.student-status-legend-small {
  font-size: 11px;
  font-weight: 600;
  padding-left: 5px;
  text-align: left;
}
.student-status-number {
  font-size: 42px;
  line-height: 1.2em;
}
.student-status-no-data {
  font-size: 18px;
  font-weight: 300;
  padding-bottom: 10px;
}
.student-status-table {
  font-size: 12px;
  line-height: 1.2em;
  margin: 10px 0;
  width: 100%;
}
.student-status-table-zebra {
  background-color: #efefef;
}
.student-status-table td {
  padding: 3px 0;
  white-space: nowrap;
}
.student-status-table th {
  padding: 15px 0 3px 0;
}
.student-status-table-icon {
  color: #999;
  padding-right: 4px;
}
</style>
