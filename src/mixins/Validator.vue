<script>
import _ from 'lodash'
import Berkeley from '@/mixins/Berkeley'
import store from '@/store'

export default {
  name: 'Validator',
  mixins: [Berkeley],
  methods: {
    validateCohortName: function(cohort) {
      const name = _.trim(cohort.name)
      const deptCodes = this.myDeptCodes(['advisor', 'director'])
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
        let all = {
          'curated group': store.getters['currentUserExtras/myCuratedGroups'],
          cohort: store.getters['currentUserExtras/myCohorts']
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
