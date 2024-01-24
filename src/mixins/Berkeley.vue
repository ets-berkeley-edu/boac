<script>
import _ from 'lodash'
import auth from '@/auth'
import store from '@/store'
import Vue from 'vue'
import {map} from 'lodash'

const getSectionsWithIncompleteStatus = sections => _.filter(sections, 'incompleteStatusCode')

const myDeptCodes = roles => {
  const departments = store.getters['context/currentUser'].departments
  return _.map(_.filter(departments, d => _.findIndex(roles, role => d.role === role) > -1), 'code')
}

export default {
  name: 'Berkeley',
  methods: {
    getAdvisorSortOrder(advisor) {
      return advisor.title && advisor.title.toLowerCase().includes('director') ? 1 : 0
    },
    getBoaUserRoles(user, department) {
      const roles = []
      if (department.role) {
        roles.push(_.upperFirst(department.role))
      }
      return roles
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
      ]
    },
    getCsvExportColumns(domain) {
      return domain === 'default' ? this.getDefaultCsvExportColumns() : this.getAdmitCsvExportColumns()
    },
    getCsvExportColumnsSelected(domain) {
      return domain === 'default' ? ['first_name', 'last_name', 'sid', 'email', 'phone'] : map(this.getCsvExportColumns(), 'value')
    },
    getDefaultCsvExportColumns() {
      const lastTermId = this.previousSisTermId(this.$config.currentEnrollmentTermId)
      const previousTermId = this.previousSisTermId(lastTermId)
      return [
        {text: 'First name', value: 'first_name'},
        {text: 'Last name', value: 'last_name'},
        {text: 'SID', value: 'sid'},
        {text: 'Email address', value: 'email'},
        {text: 'Phone number', value: 'phone'},
        {text: 'Major(s)', value: 'majors'},
        {text: 'Minor(s)', value: 'minors'},
        {text: 'Academic Subplans', value: 'subplans'},
        {text: 'Level by Units', value: 'level_by_units'},
        {text: 'Terms in attendance', value: 'terms_in_attendance'},
        {text: 'Expected Graduation Term', value: 'expected_graduation_term'},
        {text: 'Units completed', value: 'units_completed'},
        {text: `Term GPA (${this.termNameForSisId(previousTermId)})`, value: `term_gpa_${previousTermId}`},
        {text: `Term GPA (${this.termNameForSisId(lastTermId)})`, value: `term_gpa_${lastTermId}`},
        {text: 'Cumulative GPA', value: 'cumulative_gpa'},
        {text: 'Program status', value: 'program_status'},
        {text: 'Transfer status', value: 'transfer'},
        {text: 'Intended Major', value: 'intended_major'},
        {text: 'Units in progress', value: 'units_in_progress'}
      ]
    },
    getIncompleteGradeDescription: (courseDisplayName, sections) => {
      let description
      const sections_with_incomplete = getSectionsWithIncompleteStatus(sections)
      if (sections_with_incomplete.length) {
        if (sections.length === 1) {
          const section = sections[0]
          if (_.toUpper(section['incompleteFrozenFlag']) === 'Y') {
            description = 'Frozen incomplete grade will not lapse into a failing grade.'
          } else {
            const statusCode = _.toUpper(section.incompleteStatusCode)
            let lapseDate
            if (section.incompleteLapseGradeDate) {
              lapseDate = Vue.prototype.$moment(new Date(section.incompleteLapseGradeDate)).format('ll')
            }
            switch(statusCode) {
            case 'I':
              const gradingBasis = _.toUpper(section.gradingBasis)
              let outcome = 'a failing grade'
              if (['GRD', 'LETTER'].includes(gradingBasis)) {
                outcome = 'an F'
              } else if (['AUD', 'BMT', 'CNC', 'CPN', 'DPN', 'EPN', 'ESU', 'PNP', 'P/NP'].includes(gradingBasis)) {
                outcome = 'a NP'
              } else if (['NON', 'SUS'].includes(gradingBasis)) {
                outcome = 'a U'
              }
              const prefix = `Incomplete grade scheduled to become ${outcome}`
              description = lapseDate ? `${prefix} on ${lapseDate}.` : `${prefix}.`
              break
            case 'L':
              description = 'Formerly an incomplete grade' + (lapseDate ? ` on ${lapseDate}.` : '.')
              break
            case 'R':
            default:
              description = 'Formerly an incomplete grade.'
              break
            }
          }
          if (section.incompleteComments) {
            description += ` (${section.incompleteComments})`
          }
        } else {
          description = `Student has incomplete grade in ${sections.length} ${courseDisplayName} sections.`
        }
      }
      return description
    },
    getSectionsWithIncompleteStatus,
    isCoe: auth.isCoe,
    isDirector: user => !!_.size(_.filter(user.departments, d => d.role === 'director')),
    myDeptCodes,
    nextSisTermId(termId) {
      let nextTermId = ''
      let strTermId = termId.toString()
      switch (strTermId.slice(3)) {
      case '2':
        nextTermId = strTermId.slice(0, 3) + '5'
        break
      case '5':
        nextTermId = strTermId.slice(0, 3) + '8'
        break
      case '8':
        nextTermId =
          (parseInt(strTermId.slice(0, 3), 10) + 1).toString() + '2'
        break
      default:
        break
      }
      return nextTermId
    },
    previousSisTermId(termId) {
      let previousTermId = ''
      let strTermId = termId.toString()
      switch (strTermId.slice(3)) {
      case '2':
        previousTermId =
          (parseInt(strTermId.slice(0, 3), 10) - 1).toString() + '8'
        break
      case '5':
        previousTermId = strTermId.slice(0, 3) + '2'
        break
      case '8':
        previousTermId = strTermId.slice(0, 3) + '5'
        break
      default:
        break
      }
      return previousTermId
    },
    setWaitlistedStatus(course) {
      _.each(course.sections, function(section) {
        course.waitlisted =
          course.waitlisted || section.enrollmentStatus === 'W'
      })
    },
    sisIdForTermName(termName) {
      let words = _.words(termName)
      const season = words[0]
      const year = words[1]
      let termId = ''
      switch (season) {
      case 'Fall':
        termId = year.slice(0, 1) + year.slice(2, 4) + '8'
        break
      case 'Spring':
        termId = year.slice(0, 1) + year.slice(2, 4) + '2'
        break
      case 'Summer':
        termId = year.slice(0, 1) + year.slice(2, 4) + '5'
        break
      default:
        break
      }
      return termId
    },
    termNameForSisId(termId) {
      let termName = ''
      if (termId) {
        const strTermId = termId.toString()
        const century = _.startsWith(strTermId, '1') ? '19' : '20'
        termName = century + strTermId.slice(1, 3)
        switch (strTermId.slice(3)) {
        case '2':
          termName = 'Spring ' + termName
          break
        case '5':
          termName = 'Summer ' + termName
          break
        case '8':
          termName = 'Fall ' + termName
          break
        default:
          break
        }
      }
      return termName
    },
    translateSortByOption(option) {
      const translations = {
        cs_empl_id: 'CS ID',
        group_name: 'Team',
        terms_in_attendance: 'Terms in Attendance, ascending',
        'terms_in_attendance desc': 'Terms in Attendance, descending',
        gpa: 'Cumulative GPA, ascending',
        'gpa desc': 'Cumulative GPA, descending',
      }
      if (translations[option]) {
        return translations[option]
      } else if (option.startsWith('term_gpa_')) {
        const termName = this.termNameForSisId(option.substr(9,4))
        const ordering = option.endsWith('desc') ? 'descending' : 'ascending'
        return `${termName} GPA, ${ordering}`
      } else {
        return option
      }
    }
  }
}
</script>
