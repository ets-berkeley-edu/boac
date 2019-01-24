<template>
  <div>
    <Spinner/>
    <div v-if="!loading">
      <div class="flex-row full-width" id="student-profile-container">
        <div class="student-profile-photo-container" id="student-profile-photo-container">
          <StudentAvatar :student="student" size="large-padded"/>
        </div>
        <div class="student-profile-bio-container" id="student-profile-bio-container">
          <div class="student-bio-contact">
            <h1 class="student-section-header"
                id="student-name-header"
                ref="pageHeader"
                tabindex="0"
                :class="{'demo-mode-blur': user.inDemoMode}">
              {{student.name}}
            </h1>
            <h2 class="sr-only">Profile</h2>
            <div class="sr-only" v-if="student.sisProfile.preferredName !== student.name">Preferred name</div>
            <div class="student-preferred-name"
                 id="student-preferred-name"
                 :class="{'demo-mode-blur': user.inDemoMode}"
                 v-if="student.sisProfile.preferredName !== student.name">
              {{student.sisProfile.preferredName}}</div>
            <div class="student-bio-sid" id="student-bio-sid">
              SID <span :class="{'demo-mode-blur': user.inDemoMode}">{{student.sid}}</span>
            </div>
            <div>
              <i class="fas fa-envelope"></i>
              <span class="sr-only">Email</span>
              <a id="student-mailto"
                 :href="'mailto:' + student.sisProfile.emailAddress"
                 :class="{'demo-mode-blur': user.inDemoMode}">
                 {{student.sisProfile.emailAddress}}</a>
            </div>
            <div v-if="student.sisProfile.phoneNumber">
              <i class="fas fa-phone"></i>
              <span class="sr-only">Phone number</span>
              <span :class="{'demo-mode-blur': user.inDemoMode}"
                    id="student-phone-number"
                    tabindex="0">
                {{student.sisProfile.phoneNumber}}</span>
            </div>
          </div>
          <div id="student-bio-inactive" v-if="isInactive">
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
            <div class="student-bio-header">{{get(student, 'sisProfile.level.description')}}</div>
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
            <div v-if="myCuratedGroups && myCuratedGroups.length">
              <div class="student-curated-group-checkbox"
                   v-for="(curatedGroup, curatedGroupIndex) in myCuratedGroups"
                   :key="curatedGroupIndex">
                <input :id="'curated-group-checkbox-' + curatedGroupIndex"
                       type="checkbox"
                       class="student-curated-group-checkbox-input"
                       v-model="curatedGroupMemberships"
                       :value="curatedGroup.id"
                       @change="updateCuratedGroupMembership(curatedGroup)"
                       :aria-label="(curatedGroupMemberships.includes(curatedGroup.id) ? 'Remove from' : 'Add to') + ' curated group ' + curatedGroup.name"/>
                <div class="student-curated-group-checkbox-label">
                  <router-link :to="'/curated_group/' + curatedGroup.id">{{curatedGroup.name}}</router-link>
                </div>
              </div>
            </div>
            <div class="student-curated-group-checkbox" v-if="myCuratedGroups && !myCuratedGroups.length">
              <span class="faint-text">You have no curated groups.</span>
            </div>
            <div class="student-curated-group-create-new">
              <button id="create-curated-group"
                      class="btn btn-link student-curated-group-create-new-btn"
                      v-b-modal="'create-curated-group-modal'">
                <i class="fas fa-plus"></i> Create New Curated Group
              </button>
            </div>
            <b-modal id="create-curated-group-modal"
                     @shown="focusModalById('create-input')"
                     body-class="pl-0 pr-0"
                     v-model="showCreateCuratedGroupModal"
                     hide-footer
                     hide-header-close
                     title="Name Your Curated Group">
              <CreateCuratedGroupModal :sids="[]"
                                       :create="modalCreateCuratedGroup"
                                       :cancel="modalCreateCuratedGroupCancel"/>
            </b-modal>
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
              <StudentUnitsChart v-if="showUnitTotals"
                                 :currentEnrolledUnits="currentEnrolledUnits"
                                 :cumulativeUnits="cumulativeUnits">
              </StudentUnitsChart>
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
                <div class="student-status-number" v-if="student.sisProfile.cumulativeGPA">
                  {{ student.sisProfile.cumulativeGPA | round(3) }}
                </div>
                <div class="student-status-number" v-if="!student.sisProfile.cumulativeGPA">
                  -- <span class="sr-only">No data</span>
                </div>
              </div>
              <div class="student-chart-outer" id="student-status-gpa-trends">
                <div class="student-status-legend student-status-legend-heading">GPA Trends</div>
                <StudentGpaChart v-if="get(student, 'termGpa.length') > 1"
                                 :student="student">
                </StudentGpaChart>
                <div class="student-status-legend student-status-legend-small"
                     v-if="isEmpty(student.termGpa)">
                  GPA Not Yet Available
                </div>
                <div class="student-status-legend student-status-legend-gpa"
                     v-if="!isEmpty(student.termGpa)">
                  {{ student.termGpa[0].name }} GPA:
                  <strong :class="{'student-gpa-last-term': student.termGpa[0].gpa >= 2, 'student-gpa-alert': student.termGpa[0].gpa < 2}">
                    {{ student.termGpa[0].gpa | round(3) }}
                  </strong>
                </div>
                <button class="btn btn-link toggle-btn-link" @click="showTermGpa=!showTermGpa" v-if="!isEmpty(student.termGpa)">
                  <i :class="{'fas fa-caret-right': !showTermGpa, 'fas fa-caret-down': showTermGpa}"></i>
                  <span v-if="!showTermGpa">Show Term GPA</span>
                  <span v-if="showTermGpa">Hide Term GPA</span>
                </button>
              </div>
            </div>
            <table class="student-status-table" v-if="showTermGpa">
              <tr>
                <th>Term</th>
                <th>GPA</th>
              </tr>
              <tr v-for="(term, termIndex) in student.termGpa" :key="termIndex" :class="{'student-status-table-zebra': termIndex % 2 === 0}">
                <td>{{ term.name }}</td>
                <td v-if="term.gpa < 2">
                  <div class="student-gpa-term-alert-outer">
                    <i class="fa fa-exclamation-triangle student-gpa-term-alert student-gpa-term-alert-icon"></i>
                    <div class="student-gpa-term-alert">{{ term.gpa | round(3) }}</div>
                  </div>
                </td>
                <td v-if="term.gpa >= 2">{{ term.gpa | round(3) }}</td>
              </tr>
              <tr v-if="isEmpty(student.termGpa)">
                <td>No previous terms</td>
                <td>--</td>
              </tr>
            </table>
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
      <div class="student-terms-container" id="student-terms-container">
        <h2 class="student-section-header">Classes</h2>
        <div class="student-term"
             v-for="(term, index) in (showAllTerms ? student.enrollmentTerms : student.enrollmentTerms.slice(0,1))"
             :key="index">
          <div class="term-no-enrollments"
               v-if="index === 0 && !student.hasCurrentTermEnrollments && (currentEnrollmentTermId > parseInt(term.termId))">
            <h3 class="student-term-header">{{currentEnrollmentTerm}}</h3>
            <div class="term-no-enrollments-description">No enrollments</div>
            <StudentAlerts :student="student"></StudentAlerts>
          </div>

          <h3 class="student-term-header">{{term.termName}}</h3>
            <StudentAlerts :student="student"
                           v-if="index === 0 && (student.hasCurrentTermEnrollments || (currentEnrollmentTermId <= parseInt(term.termId)))">
            </StudentAlerts>
            <div v-for="(course, courseIndex) in term.enrollments" :key="courseIndex" class="student-course">
              <div class="student-course-heading">
                <div class="student-course-heading-start">
                  <div class="student-course-heading-start-inner">
                    <div class="student-course-heading-title-wrapper text-muted">
                      <span class="sr-only">Row {{courseIndex + 1}} of {{term.enrollments.length}}</span>
                      <div>
                        <h4 class="student-course-title">{{course.displayName}}</h4>
                      </div>
                      <b-btn :id="`term-${term.termId}-course-${courseIndex}-toggle`"
                             v-b-toggle="`course-canvas-data-${term.termId}-${courseIndex}`"
                             class="student-course-collapse-button"
                             variant="link">
                        <i class="when-course-closed fas fa-caret-right"></i>
                        <span class="when-course-closed sr-only">Show course details</span>
                        <i class="when-course-open fas fa-caret-down"></i>
                        <span class="when-course-open sr-only">Hide course details</span>
                      </b-btn>
                    </div>
                    <div>
                      <div class="student-course-sections">
                        <span v-for="(section, sectionIndex) in course.sections"
                              :key="sectionIndex">
                          <span v-if="section.displayName">
                            <span v-if="sectionIndex === 0">(</span><!--
                            --><router-link :id="`term-${term.termId}-section-${section.ccn}`"
                               :to="`/course/${term.termId}/${section.ccn}?u=${student.uid}`"
                               v-if="section.isViewableOnCoursePage">{{section.displayName}}</router-link><!--
                            --><span v-if="!section.isViewableOnCoursePage">
                                 {{section.displayName}}</span><!--
                            --><span v-if="sectionIndex < course.sections.length - 1"> | </span><!--
                            --><span v-if="sectionIndex === course.sections.length - 1">)</span>
                          </span>
                        </span>
                      </div>
                      <span class="student-waitlisted red-flag-status" v-if="course.waitlisted">WAITLISTED</span>
                    </div>
                  </div>
                  <div class="student-course-name">{{course.title}}</div>
                </div>
                <div class="student-course-heading-end">
                  <div class="student-course-heading-units" v-if="'units' in course">
                    {{ 'Unit' | pluralize(course.units) }}
                  </div>
                  <div class="student-course-heading-grades" v-if="'grade' in course || 'gradingBasis' in course">
                    <div class="student-course-heading-grade">
                      Final:
                      <span class="student-course-grade"
                            v-if="course.grade">{{course.grade}}</span>
                      <span class="student-course-grading-basis"
                            v-if="!course.grade">{{course.gradingBasis}}</span>
                      <span class="student-course-grade"
                            v-if="!course.grade && !course.gradingBasis"><span class="sr-only">No data</span>&mdash;</span>
                    </div>
                    <div class="student-course-heading-grade" v-if="currentEnrollmentTermId === parseInt(term.termId)">
                      Mid:
                      <span class="student-course-grade"
                            v-if="course.midtermGrade">{{course.midtermGrade}}</span>
                      <span class="student-course-grade"
                            v-if="!course.midtermGrade"><span class="sr-only">No data</span>&mdash;</span>
                    </div>
                  </div>
                </div>
              </div>
              <b-collapse class="panel-body" :id="`course-canvas-data-${term.termId}-${courseIndex}`">
                <div v-for="(canvasSite, index) in course.canvasSites" :key="index" class="student-bcourses-wrapper">
                  <h5 class="student-bcourses-site-code">
                    <span class="sr-only">Course Site</span>
                    {{canvasSite.courseCode}}
                  </h5>
                  <table class="student-bcourses">
                    <tr>
                      <th class="student-bcourses-legend" scope="row">
                        Assignments Submitted
                      </th>
                      <td class="student-bcourses-summary">
                        <span v-if="canvasSite.analytics.assignmentsSubmitted.displayPercentile">
                          <strong>{{canvasSite.analytics.assignmentsSubmitted.displayPercentile}}</strong> percentile
                        </span>
                        <span class="student-bcourses-no-data"
                              v-if="!canvasSite.analytics.assignmentsSubmitted.displayPercentile">
                          No Assignments
                        </span>
                      </td>
                      <td>
                        <span v-if="canvasSite.analytics.assignmentsSubmitted.courseDeciles">
                          Score:
                          <strong>{{canvasSite.analytics.assignmentsSubmitted.student.raw}}</strong>
                          <span class="student-bcourses-maximum">
                            (Maximum: {{canvasSite.analytics.assignmentsSubmitted.courseDeciles[10]}})
                          </span>
                        </span>
                        <span class="student-bcourses-no-data"
                              v-if="!canvasSite.analytics.assignmentsSubmitted.courseDeciles">
                          No Data
                        </span>
                      </td>
                    </tr>
                    <tr>
                      <th class="student-bcourses-legend" scope="row">
                        Assignment Grades
                      </th>
                      <td class="student-bcourses-summary">
                        <span v-if="canvasSite.analytics.currentScore.displayPercentile">
                          <strong>{{canvasSite.analytics.currentScore.displayPercentile}}</strong> percentile
                        </span>
                        <span class="student-bcourses-no-data"
                              v-if="!canvasSite.analytics.currentScore.displayPercentile">
                          No Grades
                        </span>
                      </td>
                      <td class="profile-boxplot-container">
                        <StudentBoxplot :dataset="canvasSite.analytics"
                                        :numericId="canvasSite.canvasCourseId.toString()"
                                        v-if="canvasSite.analytics.currentScore.boxPlottable"></StudentBoxplot>
                        <div class="sr-only" v-if="canvasSite.analytics.currentScore.boxPlottable">
                          <div>User score: {{canvasSite.analytics.currentScore.student.raw}}</div>
                          <div>Maximum: {{canvasSite.analytics.currentScore.courseDeciles[10]}}</div>
                          <div>70th Percentile: {{canvasSite.analytics.currentScore.courseDeciles[7]}}</div>
                          <div>50th Percentile: {{canvasSite.analytics.currentScore.courseDeciles[5]}}</div>
                          <div>30th Percentile: {{canvasSite.analytics.currentScore.courseDeciles[3]}}</div>
                          <div>Minimum: {{canvasSite.analytics.currentScore.courseDeciles[0]}}</div>
                        </div>
                        <div v-if="!canvasSite.analytics.currentScore.boxPlottable">
                          <span class="student-bcourses-no-data"
                                v-if="canvasSite.analytics.currentScore.courseDeciles">
                            Score:
                            <strong>{{canvasSite.analytics.currentScore.student.raw}}</strong>
                            <span class="student-bcourses-maximum">
                              (Maximum: {{canvasSite.analytics.currentScore.courseDeciles[10]}})
                            </span>
                          </span>
                          <span class="student-bcourses-no-data"
                                v-if="!canvasSite.analytics.currentScore.courseDeciles">
                            No Data
                          </span>
                        </div>
                       </td>
                    </tr>
                    <tr v-if="currentEnrollmentTermId === parseInt(term.termId)">
                      <th class="student-bcourses-legend" scope="row">
                        Last bCourses Activity
                      </th>
                      <td colspan="2">
                        <div v-if="!canvasSite.analytics.lastActivity.student.raw">
                          <span :class="{'demo-mode-blur': user.inDemoMode}">{{student.name}}</span> has never visited this course site.
                        </div>
                        <div v-if="canvasSite.analytics.lastActivity.student.raw">
                          <span :class="{'demo-mode-blur': user.inDemoMode}">{{student.name}}</span>
                          last visited the course site {{lastActivityDays(canvasSite.analytics).toLowerCase()}}.
                          {{lastActivityInContext(canvasSite.analytics)}}
                        </div>
                      </td>
                    </tr>
                  </table>
                </div>
                <div class="student-bcourses-wrapper student-course-notation" v-if="isEmpty(course.canvasSites)">
                  No additional information
                </div>
              </b-collapse>
            </div>
            <div class="student-course-heading student-course" v-if="term.enrolledUnits">
              <div class="student-course-heading-start"></div>
              <div class="student-course-heading-end">
                <div class="student-course-heading-units-total">
                  <div>
                    <span>Total Units </span><span :id="`term-${term.termId}-enrolled-units`">{{term.enrolledUnits}}</span>
                  </div>
                  <div class="student-course-heading-units-override"
                       v-if="currentEnrollmentTermId === parseInt(term.termId) && get(student, 'sisProfile.currentTerm.unitsMinOverride')">
                    <span>Min Approved </span><span :id="`term-${term.termId}-min-units`">{{student.sisProfile.currentTerm.unitsMinOverride}}</span>
                  </div>
                  <div class="student-course-heading-units-override"
                       v-if="currentEnrollmentTermId === parseInt(term.termId) && get(student, 'sisProfile.currentTerm.unitsMaxOverride')">
                    <span>Max Approved </span><span :id="`term-${term.termId}-max-units`">{{student.sisProfile.currentTerm.unitsMaxOverride}}</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="student-course student-course-dropped"
                 is-open="true"
                 v-if="!isEmpty(term.droppedSections)">
              <div v-for="(droppedSection, index) in term.droppedSections" :key="index">
                <div class="student-course-dropped-title">
                  {{droppedSection.displayName}} - {{droppedSection.component}} {{droppedSection.sectionNumber}}
                <div class="student-course-notation">
                  <i class="fas fa-exclamation-triangle student-course-dropped-icon"></i> Dropped
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="get(student, 'enrollmentTerms.length') > 1" class="toggle-previous-semesters-wrapper">
          <button class="btn btn-link toggle-btn-link" @click="showAllTerms=!showAllTerms">
            <i :class="{'fas fa-caret-right': !showAllTerms, 'fas fa-caret-up': showAllTerms}"></i>
            <span v-if="!showAllTerms">View Previous Semesters</span>
            <span v-if="showAllTerms">Hide Previous Semesters</span>
          </button>
        </div>
        <div v-if="isEmpty(student.enrollmentTerms)">
          No courses
          <div v-if="student.sisProfile.withdrawalCancel">
            <span class="red-flag-small">
              {{student.sisProfile.withdrawalCancel.description}} ({{student.sisProfile.withdrawalCancel.reason}}) {{student.sisProfile.withdrawalCancel.date | date}}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import _ from 'lodash';
import Context from '@/mixins/Context';
import CreateCuratedGroupModal from '@/components/curated/CreateCuratedGroupModal';
import Loading from '@/mixins/Loading';
import Spinner from '@/components/util/Spinner';
import StudentAlerts from '@/components/student/StudentAlerts';
import StudentAnalytics from '@/mixins/StudentAnalytics';
import StudentAvatar from '@/components/student/StudentAvatar';
import StudentBoxplot from '@/components/student/StudentBoxplot';
import StudentGpaChart from '@/components/student/StudentGpaChart';
import StudentMetadata from '@/mixins/StudentMetadata';
import StudentUnitsChart from '@/components/student/StudentUnitsChart';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import {
  addStudents,
  createCuratedGroup,
  getMyCuratedGroupIdsPerStudentId,
  removeFromCuratedGroup
} from '@/api/curated';
import { getStudentDetails } from '@/api/student';

export default {
  name: 'Student',
  mixins: [
    Context,
    Loading,
    StudentAnalytics,
    StudentMetadata,
    UserMetadata,
    Util
  ],
  components: {
    CreateCuratedGroupModal,
    Spinner,
    StudentAlerts,
    StudentAvatar,
    StudentBoxplot,
    StudentGpaChart,
    StudentUnitsChart
  },
  created() {
    var uid = this.$route.path.split('/').pop();
    this.loadStudent(uid);
  },
  data: () => ({
    curatedGroupMemberships: [],
    currentEnrolledUnits: undefined,
    showAllTerms: false,
    showCreateCuratedGroupModal: false,
    showTermGpa: false,
    student: {
      termGpa: []
    }
  }),
  methods: {
    loadStudent(uid) {
      getStudentDetails(uid).then(data => {
        if (data) {
          this.setPageTitle(data.name);
          _.assign(this.student, data);
          this.isInactive = this.displayAsInactive(this.student);
          this.cumulativeUnits = _.get(
            this.student,
            'sisProfile.cumulativeUnits'
          );
          this.setCurrentEnrollmentTerm();
          _.each(this.student.enrollmentTerms, this.parseEnrollmentTerm);

          getMyCuratedGroupIdsPerStudentId(this.student.sid).then(data => {
            this.curatedGroupMemberships = data;
          });
          this.loaded();
        } else {
          this.$router.push({ path: '/404' });
        }
      });
    },
    modalCreateCuratedGroup(name) {
      this.showCreateCuratedGroupModal = false;
      createCuratedGroup(name, []);
    },
    modalCreateCuratedGroupCancel() {
      this.showCreateCuratedGroupModal = false;
    },
    parseEnrollmentTerm(term) {
      // Merge in unmatched canvas sites
      const unmatched = _.map(term.unmatchedCanvasSites, function(c) {
        // course_code is often valuable (eg, 'ECON 1 - LEC 001'), occasionally not (eg, CCN). Use it per strict criteria:
        const useCourseCode = /^[A-Z].*[A-Za-z]{3} \d/.test(c.courseCode);
        return _.merge(c, {
          displayName: useCourseCode ? c.courseCode : c.courseName,
          title: useCourseCode ? c.courseName : null,
          canvasSites: [c]
        });
      });
      term.enrollments = _.concat(term.enrollments, unmatched);
      _.each(term.enrollments, function(course) {
        _.each(course.sections, function(section) {
          course.waitlisted =
            course.waitlisted || section.enrollmentStatus === 'W';
          course.isOpen = false;
          section.displayName = section.component + ' ' + section.sectionNumber;
          section.isViewableOnCoursePage = section.primary;
        });
      });
      if (_.get(term, 'termGpa.unitsTakenForGpa')) {
        this.student.termGpa.push({
          name: _.get(term, 'termName'),
          gpa: _.get(term, 'termGpa.gpa')
        });
      }
    },
    setCurrentEnrollmentTerm() {
      const currentEnrollmentTerm = _.find(
        _.get(this.student, 'enrollmentTerms'),
        {
          termId: this.currentEnrollmentTermId.toString()
        }
      );
      if (currentEnrollmentTerm) {
        this.currentEnrolledUnits = _.get(
          currentEnrollmentTerm,
          'enrolledUnits'
        );
      }
      this.showUnitTotals = this.cumulativeUnits || this.currentEnrolledUnits;
    },
    updateCuratedGroupMembership(group) {
      if (_.includes(this.curatedGroupMemberships, group.id)) {
        addStudents(group, [this.student.sid]);
      } else {
        removeFromCuratedGroup(group.id, this.student.sid);
      }
    }
  }
};
</script>

<style scoped>
.collapsed > .when-course-open,
:not(.collapsed) > .when-course-closed {
  display: none;
}
.student-bcourses {
  line-height: 1.1;
  margin-bottom: 20px;
  width: 80%;
}
.student-bcourses td,
.student-bcourses th {
  font-size: 14px;
  padding: 0 25px 5px 0;
  text-align: left;
  vertical-align: top;
}
.student-bcourses-legend {
  color: #999;
  font-weight: normal;
  white-space: nowrap;
  width: 15em;
}
.student-bcourses-maximum {
  color: #666;
}
.student-bcourses-no-data {
  color: #666;
  font-style: italic;
}
.student-bcourses-site-code {
  font-size: 15px;
  margin-bottom: 5px;
}
.student-bcourses-summary {
  width: 12em;
}
.student-bcourses-wrapper {
  margin-top: 15px;
}
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
.student-course {
  border-top: 1px solid #999;
  margin-top: 20px;
}
.student-course-collapse-button {
  color: #337ab7;
  height: 15px;
  line-height: 1;
  margin-right: 10px;
  padding: 0;
  width: 12px;
}
.student-course-dropped {
  margin-top: 15px;
  padding-top: 15px;
}
.student-course-dropped-icon {
  color: #f0ad4e;
}
.student-course-dropped-title {
  font-weight: bold;
}
.student-course-grade {
  font-weight: bold;
}
.student-course-grading-basis {
  font-style: italic;
}
.student-course-heading {
  color: #777;
  display: flex;
  justify-content: space-between;
  flex-direction: row;
  font-weight: 500;
  line-height: 1.1;
  margin-top: 15px;
  width: 100%;
}
.student-course-heading.student-course .student-course-heading-end {
  flex: 0 0 290px;
}
.student-course-heading-end {
  display: flex;
  flex: 0 0 200px;
}
.student-course-heading-grade {
  white-space: nowrap;
}
.student-course-heading-grades {
  display: flex;
  flex: 0 0 100px;
  flex-direction: column;
}
.student-course-heading-start {
  display: flex;
  flex-direction: column;
}
.student-course-heading-start-inner {
  align-items: baseline;
  display: flex;
  justify-content: flex-start;
}
.student-course-heading-title-wrapper {
  display: flex;
  flex-direction: row-reverse;
}
.student-course-heading-units {
  flex: 0 0 100px;
  white-space: nowrap;
}
.student-course-heading-units-override {
  font-size: 16px;
  font-weight: 400;
}
.student-course-heading-units-total {
  color: #777;
  display: flex;
  flex-direction: column;
  font-size: 16px;
  font-weight: 500;
  margin-top: 15px;
  flex: 0 0 142px;
}
.student-course-heading-units-total > div {
  display: flex;
  justify-content: space-between;
}
.student-course-name {
  font-size: 16px;
  font-weight: 400;
  margin: 5px 0 0;
}
.student-course-notation {
  color: #999;
  margin-bottom: 10px;
}
.student-course-title {
  font-size: 16px;
  margin: 0;
  padding-right: 5px;
  white-space: nowrap;
}
.student-course-sections {
  display: inline-block;
  font-weight: 400;
  white-space: nowrap;
}
.student-curated-group-checkbox {
  align-items: center;
  display: flex;
  font-size: 12px;
  padding: 1px;
}
.student-curated-group-checkbox-input {
  flex: 0 0 12px;
}
.student-curated-group-checkbox-label {
  margin-left: 5px;
}
.student-curated-group-checkbox-primary-label {
  font-weight: bold;
}
.student-curated-group-create-new {
  border-top: solid 1px #ccc;
  font-size: 11px;
  margin-top: 5px;
  padding: 3px 1px 1px 1px;
}
.student-curated-group-create-new-btn {
  border: 0;
  font-size: 11px;
  padding: 0;
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
.student-gpa-alert {
  color: #d0021b;
}
.student-gpa-last-term {
  color: #000;
  font-weight: 700;
}
.student-gpa-last-term-outer {
  font-size: 12px;
  padding-left: 5px;
  text-align: left;
}
.student-gpa-term-alert {
  color: #d0021b;
  position: relative;
  right: 20px;
}
.student-gpa-term-alert-icon {
  width: 20px;
}
.student-gpa-term-alert-outer {
  display: flex;
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
  min-width: 340px;
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
.student-status-legend-gpa {
  font-size: 12px;
  padding-left: 5px;
  text-align: right;
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
  text-align: left;
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
.student-term {
  margin: 30px 0 10px 0;
}
.student-term-header {
  font-size: 20px;
  font-weight: 400;
  margin: 20px 0 15px 0;
  color: #999;
}
.student-terms-container {
  margin: 20px;
}
.toggle-previous-semesters-wrapper {
  text-align: center;
}
</style>
