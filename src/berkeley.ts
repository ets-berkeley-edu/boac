import _ from 'lodash'
import moment from 'moment'
import {useContextStore} from '@/stores/context'

export function describeCuratedGroupDomain(domain, capitalize) {
  const format = s => capitalize ? _.capitalize(s) : s
  return format(domain === 'admitted_students' ? 'admissions ' : 'curated ') + format('group')
}

export function displayAsAscInactive(student) {
  return (
    _.includes(myDeptCodes(['advisor', 'director']), 'UWASC') &&
    _.get(student, 'athleticsProfile') &&
    !_.get(student, 'athleticsProfile.isActiveAsc')
  )
}

export function displayAsCoeInactive(student) {
  return (
    _.includes(myDeptCodes(['advisor', 'director']), 'COENG') &&
    _.get(student, 'coeProfile') &&
    !_.get(student, 'coeProfile.isActiveCoe')
  )
}

export function getAdmitCsvExportColumns() {
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
}

export function getBoaUserRoles(user, department) {
  const roles: string[] = []
  if (department.role) {
    roles.push(_.upperFirst(department.role))
  }
  return roles
}

export function getCsvExportColumns(domain) {
  return domain === 'default' ? getDefaultCsvExportColumns() : getAdmitCsvExportColumns()
}

export function getCsvExportColumnsSelected(domain) {
  return domain === 'default' ? ['first_name', 'last_name', 'sid', 'email', 'phone'] : _.map(getAdmitCsvExportColumns(), 'value')
}

export function getDefaultCsvExportColumns() {
  const lastTermId = previousSisTermId(_.get(useContextStore().config, 'currentEnrollmentTermId'))
  const previousTermId = previousSisTermId(lastTermId)
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
    {text: `Term GPA (${termNameForSisId(previousTermId)})`, value: `term_gpa_${previousTermId}`},
    {text: `Term GPA (${termNameForSisId(lastTermId)})`, value: `term_gpa_${lastTermId}`},
    {text: 'Cumulative GPA', value: 'cumulative_gpa'},
    {text: 'Program status', value: 'program_status'},
    {text: 'Transfer status', value: 'transfer'},
    {text: 'Intended Major', value: 'intended_major'},
    {text: 'Units in progress', value: 'units_in_progress'}
  ]
}

export function getIncompleteGradeDescription(courseDisplayName, sections) {
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
          lapseDate = moment(new Date(section.incompleteLapseGradeDate)).format('ll')
        }
        switch(statusCode) {
        case 'I': {
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
        }
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
}

export function getMatrixPlottableProperty(obj, prop) {
  if (_.has(obj, prop + '.percentile')) {
    return _.get(obj, prop + '.percentile')
  }
  return _.get(obj, prop)
}

export function getSectionsWithIncompleteStatus(sections) {
  return _.filter(sections, 'incompleteStatusCode')
}

export function hasMatrixPlottableProperty(obj, prop) {
  // In the case of cumulative GPA, zero indicates missing data rather than a real zero.
  if (prop === 'cumulativeGPA') {
    return !!getMatrixPlottableProperty(obj, prop)
  }
  return _.isFinite(getMatrixPlottableProperty(obj, prop))
}

export function isAdvisor(user) {
  return !!_.size(_.filter(user.departments, d => d.role === 'advisor'))
}

export function isAlertGrade(grade) {
  // Grades deserving alerts: D(+/-), F, I, NP, RD.
  return grade && /^[DFINR]/.test(grade)
}

export function isCoe(user) {
  return !!_.size(_.filter(user.departments, d => d.code === 'COENG' && _.includes(['advisor', 'director'], d.role)))
}

export function isDirector(user) {
  return !!_.size(_.filter(user.departments, d => d.role === 'director'))
}

export function lastActivityDays(analytics) {
  const timestamp = parseInt(_.get(analytics, 'lastActivity.student.raw'), 10)
  if (!timestamp || isNaN(timestamp)) {
    return 'Never'
  }
  // Days tick over at midnight according to the user's browser.
  const daysSince = Math.round(
    (new Date().setHours(0, 0, 0, 0) -
      new Date(timestamp * 1000).setHours(0, 0, 0, 0)) /
      86400000
  )
  switch (daysSince) {
  case 0:
    return 'Today'
  case 1:
    return 'Yesterday'
  default:
    return daysSince + ' days ago'
  }
}

export function myDeptCodes(roles) {
  const departments = _.get(useContextStore().currentUser, 'departments')
  return _.map(_.filter(departments, (d: any) => _.findIndex(roles, role => d.role === role) > -1), 'code')
}

export function isGraduate(student) {
  return _.get(student, 'sisProfile.level.description') === 'Graduate'
}

export function previousSisTermId(termId) {
  let previousTermId = ''
  const term = termId.toString()
  switch (term.slice(3)) {
  case '2':
    previousTermId =
      (parseInt(term.slice(0, 3), 10) - 1).toString() + '8'
    break
  case '5':
    previousTermId = term.slice(0, 3) + '2'
    break
  case '8':
    previousTermId = term.slice(0, 3) + '5'
    break
  default:
    break
  }
  return previousTermId
}
export function setWaitlistedStatus(course) {
  _.each(course.sections, function(section) {
    course.waitlisted = course.waitlisted || section.enrollmentStatus === 'W'
  })
}

export function sisIdForTermName(termName) {
  const words = _.words(termName)
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
}

export function termNameForSisId(termId) {
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
}

export function translateSortByOption(option) {
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
    const termName = termNameForSisId(option.substr(9,4))
    const ordering = option.endsWith('desc') ? 'descending' : 'ascending'
    return `${termName} GPA, ${ordering}`
  } else {
    return option.replaceAll('_', ' ')
  }
}
