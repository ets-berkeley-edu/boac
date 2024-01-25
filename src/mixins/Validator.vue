<script>
import _ from 'lodash'
import store from '@/store'
import {myDeptCodes} from '@/berkeley'

export default {
  name: 'Validator',
  data: () => ({
    error: undefined,
    warning: undefined
  }),
  methods: {
    clearErrors() {
      this.error = null
      this.warning = null
    },
    validateCohortName: function(cohort) {
      const name = _.trim(cohort.name)
      const deptCodes = myDeptCodes(['advisor', 'director'])
      const isReservedName = name =>
        _.includes(deptCodes, 'UWASC') &&
        _.includes(['intensive students', 'inactive students'], name.toLowerCase())
      let msg = null
      if (_.isEmpty(name)) {
        msg = 'Required'
      } else if (_.size(name) > 255) {
        msg = 'Name must be 255 characters or fewer'
      } else if (isReservedName(name)) {
        msg = `Sorry, '${name}' is a reserved name. Please choose a different name.`
      } else {
        const currentUser = store.getters['context/currentUser']
        const all = {
          'curated group': currentUser.myCuratedGroups,
          cohort: currentUser.myCohorts
        }
        _.each(all, (cohorts, cohortType) => {
          _.each(cohorts, existing => {
            if (
              (!cohort['id'] || cohort.id !== existing.id) &&
              name.toUpperCase() === existing.name.toUpperCase()
            ) {
              msg = `You have an existing ${cohortType} with this name. Please choose a different name.`
              return false
            }
          })
        })
      }
      return msg
    },
    validateSids: function(sids) {
      this.clearErrors()
      const trimmed = _.trim(sids, ' ,\n\t')
      if (trimmed) {
        const split = _.split(trimmed, /[,\r\n\t ]+/)
        if (split.length && split[0].length > 10) {
          this.error = 'SIDs must be separated by commas, line breaks, or tabs.'
          return false
        }
        const notNumeric = _.partition(split, sid => /^\d+$/.test(_.trim(sid)))[1]
        if (notNumeric.length) {
          this.error = 'Each SID must be numeric.'
        } else {
          return split
        }
      } else {
        this.warning = 'Please provide one or more SIDs.'
      }
      return false
    },
    validateTemplateTitle: template => {
      const title = _.trim(template.title)
      let msg = null
      if (_.isEmpty(title)) {
        msg = 'Required'
      } else if (_.size(title) > 255) {
        msg = 'Name must be 255 characters or fewer'
      } else {
        const myTemplates = store.getters['noteEditSession/noteTemplates']
        _.each(myTemplates, existing => {
          if (
            (!template.id || template.id !== existing.id) &&
            title.toUpperCase() === existing.title.toUpperCase()
          ) {
            msg = 'You have an existing template with this name. Please choose a different name.'
            return false
          }
        })
      }
      return msg
    }
  }
}
</script>
