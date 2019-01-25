<template>
  <div>
    <Spinner/>
    <div v-if="!loading">
      <div class="d-flex light-blue-background p-3">
        <div>
          <StudentAvatar class="pr-3" :student="student" size="large"/>
          <StudentProfileCuratedGroups :sid="student.sid"/>
        </div>
        <div>
          <div>
            <h1 id="student-name-header"
                class="student-section-header mb-1"
                ref="pageHeader"
                tabindex="0"
                :class="{'demo-mode-blur': user.inDemoMode}">
              {{ student.name }}
            </h1>
            <h2 class="sr-only">Profile</h2>
            <div class="sr-only"
                 v-if="student.sisProfile.preferredName !== student.name">Preferred name</div>
            <div id="student-preferred-name"
                 class="student-preferred-name"
                 :class="{'demo-mode-blur': user.inDemoMode}"
                 v-if="student.sisProfile.preferredName !== student.name">
              {{ student.sisProfile.preferredName }}</div>
            <div id="student-bio-sid" class="student-bio-sid font-weight-bold pb-2">
              SID <span :class="{'demo-mode-blur': user.inDemoMode}">{{ student.sid }}</span>
            </div>
            <div>
              <i class="fas fa-envelope"></i>
              <span class="sr-only">Email</span>
              <a id="student-mailto"
                 :href="`mailto:${student.sisProfile.emailAddress}`"
                 :class="{'demo-mode-blur': user.inDemoMode}">
                 {{ student.sisProfile.emailAddress }}</a>
            </div>
            <div v-if="student.sisProfile.phoneNumber">
              <i class="fas fa-phone"></i>
              <span class="sr-only">Phone number</span>
              <span id="student-phone-number"
                    :class="{'demo-mode-blur': user.inDemoMode}"
                    tabindex="0">
                {{ student.sisProfile.phoneNumber }}</span>
            </div>
          </div>
          <div id="student-bio-inactive" v-if="isInactive">
            <div class="student-bio-header student-bio-inactive">Inactive</div>
          </div>
          <div id="student-bio-athletics" v-if="student.athleticsProfile">
            <div v-for="membership in student.athleticsProfile.athletics" :key="membership.groupName">
              <div class="student-bio-header">{{ membership.groupName }}</div>
            </div>
          </div>
        </div>
        <div class="ml-auto mr-5">
          <div id="student-bio-majors">
            <h3 class="sr-only">Major</h3>
            <div v-for="plan in student.sisProfile.plans" :key="plan.description">
              <div class="student-bio-header">
                <span v-if="!plan.degreeProgramUrl">{{ plan.description }}</span>
                <a :href="plan.degreeProgramUrl"
                   target="_blank"
                   :aria-label="`Open ${plan.description} program page in new window`"
                   v-if="plan.degreeProgramUrl">
                   {{ plan.description }}</a>
              </div>
              <div class="student-bio-details" v-if="plan.program">
                {{ plan.program }}
              </div>
            </div>
          </div>
          <div id="student-bio-level">
            <h3 class="sr-only">Level</h3>
            <div class="student-bio-header">{{ get(student, 'sisProfile.level.description') }}</div>
          </div>
          <div>
            <div id="student-bio-terms-in-attendance"
                 class="student-bio-details"
                 v-if="student.sisProfile.termsInAttendance">
              {{ 'Term' | pluralize(student.sisProfile.termsInAttendance) }} in Attendance
            </div>
            <div class="student-bio-details"
                 id="student-bio-expected-graduation"
                 v-if="student.sisProfile.expectedGraduationTerm && student.sisProfile.level.code !== 'GR'">
              Expected graduation {{ student.sisProfile.expectedGraduationTerm.name }}
            </div>
          </div>
        </div>
      </div>
      <div class="flex-row full-width">
        <div class="flex-row">
          <h2 class="sr-only">Academic Status</h2>
          <div class="flex-row student-status-box">
            <h3 class="sr-only">Units</h3>
            <div id="student-status-units-completed">
              <div class="student-status-legend">Units Completed</div>
              <div class="student-status-number" v-if="cumulativeUnits">{{cumulativeUnits}}</div>
              <div class="student-status-number" v-if="!cumulativeUnits">--<span class="sr-only">No data</span></div>
            </div>
            <div id="student-status-unit-totals" class="student-chart-outer">
              <div class="student-status-legend student-status-legend-heading" aria-hidden="true">Unit Totals</div>
              <StudentUnitsChart :currentEnrolledUnits="currentEnrolledUnits"
                                 :cumulativeUnits="cumulativeUnits"
                                 v-if="showUnitTotals"/>
              <div class="student-status-legend student-status-legend-small"
                   v-if="!showUnitTotals">
                  Units Not Yet Available
              </div>
              <div id="student-status-currently-enrolled-units"
                   class="sr-only"
                   v-if="showUnitTotals">
                Currently enrolled units: {{ currentEnrolledUnits || '0' }}
              </div>
            </div>
          </div>
          <div class="student-status-box">
            <h3 class="sr-only">GPA</h3>
            <StudentProfileGPA :student="student"/>
          </div>
        </div>
      </div>
      <div>
        <AcademicTimeline :student="student"/>
      </div>
      <div>
        <h2 class="student-section-header">Classes</h2>
        <div v-for="(term, index) in (showAllTerms ? student.enrollmentTerms : student.enrollmentTerms.slice(0,1))"
             :key="index">
          <div class="term-no-enrollments"
               v-if="index === 0 && !student.hasCurrentTermEnrollments && (currentEnrollmentTermId > parseInt(term.termId))">
            <h3 class="student-term-header">{{ currentEnrollmentTerm }}</h3>
            <div class="term-no-enrollments-description">No enrollments</div>
          </div>
          <h3 class="student-term-header">{{ term.termName }}</h3>
            <div v-for="(course, courseIndex) in term.enrollments" :key="courseIndex" class="student-course">
              <div class="student-course-heading">
                <div>
                  <div>
                    <div class="text-muted">
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
                <div>
                  <div class="no-wrap" v-if="'units' in course">
                    {{ 'Unit' | pluralize(course.units) }}
                  </div>
                  <div v-if="'grade' in course || 'gradingBasis' in course">
                    <div class="no-wrap">
                      Final:
                      <span class="font-weight-bold"
                            v-if="course.grade">{{course.grade}}</span>
                      <span class="font-italic"
                            v-if="!course.grade">{{course.gradingBasis}}</span>
                      <span class="font-weight-bold"
                            v-if="!course.grade && !course.gradingBasis"><span class="sr-only">No data</span>&mdash;</span>
                    </div>
                    <div class="no-wrap" v-if="currentEnrollmentTermId === parseInt(term.termId)">
                      Mid:
                      <span class="font-weight-bold"
                            v-if="course.midtermGrade">{{course.midtermGrade}}</span>
                      <span class="font-weight-bold"
                            v-if="!course.midtermGrade"><span class="sr-only">No data</span>&mdash;</span>
                    </div>
                  </div>
                </div>
              </div>
              <b-collapse class="panel-body" :id="`course-canvas-data-${term.termId}-${courseIndex}`">
                <div v-for="(canvasSite, index) in course.canvasSites" :key="index">
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
                        <span class="font-italic text-muted"
                              v-if="!canvasSite.analytics.assignmentsSubmitted.displayPercentile">
                          No Assignments
                        </span>
                      </td>
                      <td>
                        <span v-if="canvasSite.analytics.assignmentsSubmitted.courseDeciles">
                          Score:
                          <strong>{{canvasSite.analytics.assignmentsSubmitted.student.raw}}</strong>
                          <span class="text-muted">
                            (Maximum: {{canvasSite.analytics.assignmentsSubmitted.courseDeciles[10]}})
                          </span>
                        </span>
                        <span class="font-italic text-muted"
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
                        <span class="font-italic text-muted"
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
                          <span class="font-italic text-muted"
                                v-if="canvasSite.analytics.currentScore.courseDeciles">
                            Score:
                            <strong>{{canvasSite.analytics.currentScore.student.raw}}</strong>
                            <span class="text-muted">
                              (Maximum: {{canvasSite.analytics.currentScore.courseDeciles[10]}})
                            </span>
                          </span>
                          <span class="font-italic text-muted"
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
                <div class="student-course-notation" v-if="isEmpty(course.canvasSites)">
                  No additional information
                </div>
              </b-collapse>
            </div>
            <div class="student-course-heading student-course" v-if="term.enrolledUnits">
              <div></div>
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
            <div class="student-course"
                 is-open="true"
                 v-if="!isEmpty(term.droppedSections)">
              <div v-for="(droppedSection, index) in term.droppedSections" :key="index">
                <div class="font-weight-bold">
                  {{droppedSection.displayName}} - {{droppedSection.component}} {{droppedSection.sectionNumber}}
                <div class="student-course-notation">
                  <i class="fas fa-exclamation-triangle student-course-dropped-icon"></i> Dropped
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="get(student, 'enrollmentTerms.length') > 1">
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
import AcademicTimeline from '@/components/student/AcademicTimeline';
import Context from '@/mixins/Context';
import StudentProfileCuratedGroups from '@/components/curated/StudentProfileCuratedGroups';
import Loading from '@/mixins/Loading';
import Spinner from '@/components/util/Spinner';
import StudentAnalytics from '@/mixins/StudentAnalytics';
import StudentAvatar from '@/components/student/StudentAvatar';
import StudentBoxplot from '@/components/student/StudentBoxplot';
import StudentMetadata from '@/mixins/StudentMetadata';
import StudentProfileGPA from '@/components/student/StudentProfileGPA';
import StudentUnitsChart from '@/components/student/StudentUnitsChart';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
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
    AcademicTimeline,
    StudentProfileCuratedGroups,
    Spinner,
    StudentAvatar,
    StudentBoxplot,
    StudentProfileGPA,
    StudentUnitsChart
  },
  created() {
    const uid = this.get(this.$route, 'params.uid');
    this.loadStudent(uid);
  },
  data: () => ({
    currentEnrolledUnits: undefined,
    showAllTerms: false,
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

          this.loaded();
        } else {
          this.$router.push({ path: '/404' });
        }
      });
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
  width: 80%;
}
.student-bcourses td,
.student-bcourses th {
  font-size: 14px;
}
.student-bcourses-legend {
  color: #999;
  font-weight: normal;
  white-space: nowrap;
  width: 15em;
}
.student-bcourses-site-code {
  font-size: 15px;
}
.student-bcourses-summary {
  width: 12em;
}
.student-bio-details {
  color: #999;
  font-size: 14px;
}
.student-bio-header {
  font-size: 16px;
  font-weight: 600;
}
.student-bio-inactive {
  color: #cf1715;
  text-transform: uppercase;
}
.student-bio-sid {
  font-size: 14px;
}
.student-chart-outer {
  border-left: 1px solid #999;
}
.student-course {
  border-top: 1px solid #999;
}
.student-course-collapse-button {
  color: #337ab7;
  height: 15px;
  line-height: 1;
  width: 12px;
}
.student-course-dropped-icon {
  color: #f0ad4e;
}
.student-course-heading {
  color: #777;
  font-weight: 500;
  line-height: 1.1;
  width: 100%;
}
.student-course-heading-units-override {
  font-size: 16px;
  font-weight: 400;
}
.student-course-heading-units-total {
  color: #777;
  font-size: 16px;
  font-weight: 500;
}
.student-course-name {
  font-size: 16px;
  font-weight: 400;
}
.student-course-notation {
  color: #999;
}
.student-course-title {
  font-size: 16px;
  white-space: nowrap;
}
.student-course-sections {
  display: inline-block;
  font-weight: 400;
  white-space: nowrap;
}
.student-gpa-alert {
  color: #d0021b;
}
.student-gpa-last-term {
  color: #000;
  font-weight: 700;
}
.student-gpa-term-alert {
  color: #d0021b;
  position: relative;
  right: 20px;
}
.student-gpa-term-alert-icon {
  width: 20px;
}
.student-preferred-name {
  font-size: 20px;
  font-weight: 400;
}
.light-blue-background {
  background: #e3f5ff;
}
.student-section-header {
  font-size: 24px;
  font-weight: bold;
}
.student-status-box {
  border: solid 1px #999;
  border-radius: 10px;
  font-size: 20px;
  font-weight: 400;
}
.student-status-legend {
  color: #999;
  font-size: 13px;
  font-weight: 300;
  text-transform: uppercase;
}
.student-status-legend-gpa {
  font-size: 12px;
  text-align: right;
}
.student-status-legend-heading {
  color: #000;
  font-weight: 600;
}
.student-status-legend-small {
  font-size: 11px;
  font-weight: 600;
}
.student-status-number {
  font-size: 42px;
  line-height: 1.2em;
}
.student-term-header {
  font-size: 20px;
  font-weight: 400;
  color: #999;
}
.term-no-enrollments {
  border-bottom: 1px solid #999;
}
.term-no-enrollments-description {
  border-top: 1px solid #999;
}
</style>
