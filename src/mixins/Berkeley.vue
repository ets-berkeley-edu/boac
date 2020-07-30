<script>
import _ from 'lodash';
import Vue from 'vue';

export default {
  name: 'Berkeley',
  methods: {
    getBoaUserRoles(user, department) {
      const roles = [];
      const dropInAdvisorStatus = _.find(user.dropInAdvisorStatus, ['deptCode', department.code]);
      if (department.role) {
        roles.push(_.upperFirst(department.role));
      }
      if (dropInAdvisorStatus) {
        roles.push('Drop-in Advisor');
      }
      return roles;
    },
    getAdmitCsvExportColumns() {
      return [
        {text: 'First name', value: 'first_name'},
        {text: 'Middle name', value: 'middle_name'},
        {text: 'Last name', value: 'last_name'},
        {text: 'CS ID', value: 'cs_empl_id'},
        {text: 'ApplyUC CPID', value: 'applyuc_cpid'},
        {text: 'UID', value: 'uid'},
        {text: 'Birthdate', value: 'birthdate'},
        {text: 'Freshman or Transfer', value: 'freshman_or_transfer'},
        {text: 'Admit Status', value: 'admit_status'},
        {text: 'SIR', value: 'current_sir'},
        {text: 'College', value: 'college'},
        {text: 'Admit Term', value: 'admit_term'},
        {text: 'Street 1', value: 'permanent_street_1'},
        {text: 'Street 2', value: 'permanent_street_2'},
        {text: 'City', value: 'permanent_city'},
        {text: 'Region', value: 'permanent_region'},
        {text: 'Postal Code', value: 'permanent_postal'},
        {text: 'Country', value: 'permanent_country'},
        {text: 'Sex', value: 'sex'},
        {text: 'Gender Identity', value: 'gender_identity'},
        {text: 'XEthnic', value: 'xethnic'},
        {text: 'Hispanic', value: 'hispanic'},
        {text: 'UREM', value: 'urem'},
        {text: 'Residency Category', value: 'residency_category'},
        {text: 'US Citizenship Status', value: 'us_citizenship_status'},
        {text: 'US Non Citizen Status', value: 'us_non_citizen_status'},
        {text: 'Citizenship Country', value: 'citizenship_country'},
        {text: 'Permanent Residence Country', value: 'permanent_residence_country'},
        {text: 'Non Immigrant Visa Current', value: 'non_immigrant_visa_current'},
        {text: 'Non Immigrant Visa Planned', value: 'non_immigrant_visa_planned'},
        {text: 'First Generation College', value: 'first_generation_college'},
        {text: 'Parent 1 Education', value: 'parent_1_education_level'},
        {text: 'Parent 2 Education', value: 'parent_2_education_level'},
        {text: 'Highest Parent Education', value: 'highest_parent_education_level'},
        {text: 'HS Unweighted GPA', value: 'hs_unweighted_gpa'},
        {text: 'HS Weighted GPA', value: 'hs_weighted_gpa'},
        {text: 'Transfer GPA', value: 'transfer_gpa'},
        {text: 'ACT Composite', value: 'act_composite'},
        {text: 'ACT Math', value: 'act_math'},
        {text: 'ACT English', value: 'act_english'},
        {text: 'ACT Reading', value: 'act_reading'},
        {text: 'ACT Writing', value: 'act_writing'},
        {text: 'SAT Total', value: 'sat_total'},
        {text: 'SAT Evidence-Based Reading and Writing', value: 'sat_r_evidence_based_rw_section'},
        {text: 'SAT Math', value: 'sat_r_math_section'},
        {text: 'SAT Essay Reading', value: 'sat_r_essay_reading'},
        {text: 'SAT Essay Analysis', value: 'sat_r_essay_analysis'},
        {text: 'SAT Essay Writing', value: 'sat_r_essay_writing'},
        {text: 'Waiver', value: 'application_fee_waiver_flag'},
        {text: 'Foster Care', value: 'foster_care_flag'},
        {text: 'Family Is Single Parent', value: 'family_is_single_parent'},
        {text: 'Student Is Single Parent', value: 'student_is_single_parent'},
        {text: 'Family Dependents', value: 'family_dependents_num'},
        {text: 'Student Dependents', value: 'student_dependents_num'},
        {text: 'Family Income', value: 'family_income'},
        {text: 'Student Income', value: 'student_income'},
        {text: 'Military Dependent', value: 'is_military_dependent'},
        {text: 'Military', value: 'military_status'},
        {text: 'Re-entry', value: 'reentry_status'},
        {text: 'Athlete', value: 'athlete_status'},
        {text: 'Summer Bridge', value: 'summer_bridge_status'},
        {text: 'Last School LCFF+', value: 'last_school_lcff_plus_flag'},
        {text: 'CEP', value: 'special_program_cep'}
      ];
    },
    getDefaultCsvExportColumns() {
      return [
        {text: 'First name', value: 'first_name'},
        {text: 'Last name', value: 'last_name'},
        {text: 'SID', value: 'sid'},
        {text: 'Email address', value: 'email'},
        {text: 'Phone number', value: 'phone'},
        {text: 'Major(s)', value: 'majors'},
        {text: 'Minor(s)', value: 'minors'},
        {text: 'Level by Units', value: 'level_by_units'},
        {text: 'Terms in attendance', value: 'terms_in_attendance'},
        {text: 'Expected Graduation Term', value: 'expected_graduation_term'},
        {text: 'Units completed', value: 'units_completed'},
        {text: 'Term GPA', value: 'term_gpa'},
        {text: 'Cumulative GPA', value: 'cumulative_gpa'},
        {text: 'Program status', value: 'program_status'}
      ];
    },
    isDirector: (user) => {
      return !!_.size(_.filter(user.departments, d => d.role === 'director'));
    },
    myDeptCodes: (roles) => {
      return _.map(_.filter(Vue.prototype.$currentUser.departments, d => _.findIndex(roles, role => d.role === role) > -1), 'code');
    },
    previousSisTermId(termId) {
      let previousTermId = '';
      let strTermId = termId.toString();
      switch (strTermId.slice(3)) {
        case '2':
          previousTermId =
            (parseInt(strTermId.slice(0, 3), 10) - 1).toString() + '8';
          break;
        case '5':
          previousTermId = strTermId.slice(0, 3) + '2';
          break;
        case '8':
          previousTermId = strTermId.slice(0, 3) + '5';
          break;
        default:
          break;
      }
      return previousTermId;
    },
    setWaitlistedStatus(course) {
      _.each(course.sections, function(section) {
        course.waitlisted =
          course.waitlisted || section.enrollmentStatus === 'W';
      });
    },
    termNameForSisId(termId) {
      let termName = '';
      if (termId) {
        const strTermId = termId.toString();
        termName = '20' + strTermId.slice(1, 3);
        switch (strTermId.slice(3)) {
          case '2':
            termName = 'Spring ' + termName;
            break;
          case '5':
            termName = 'Summer ' + termName;
            break;
          case '8':
            termName = 'Fall ' + termName;
            break;
          default:
            break;
        }
      }
      return termName;
    }
  }
};
</script>
