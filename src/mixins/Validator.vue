<script>
import _ from 'lodash'
import Berkeley from '@/mixins/Berkeley'
import {validateSids} from '@/api/student'
import store from '@/store'

export default {
  name: 'Validator',
  mixins: [Berkeley],
  data: () => ({
    error: undefined,
    isValidating: false,
    warning: undefined
  }),
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
    validateSids: function(sids) {
      return new Promise(resolve => {
        const validSids = []
        const trimmed = _.trim(sids, ' ,\n\t')
        if (trimmed) {
          const split = _.split(trimmed, /[,\r\n\t ]+/)
          const notNumeric = _.partition(split, sid => /^\d+$/.test(_.trim(sid)))[1]
          if (notNumeric.length) {
            this.error = 'SIDs must be separated by commas, line breaks, or tabs.'
          } else {
            this.isValidating = true
            validateSids(split).then(data => {
              const notFound = []
              _.each(data, entry => {
                switch(entry.status) {
                case 200:
                case 401:
                  validSids.push(entry.sid)
                  break
                default:
                  notFound.push(entry.sid)
                }
              })
              this.isValidating = false
              if (notFound.length === 1) {
                this.warning = `Student ${notFound[0]} not found.`
              } else if (notFound.length > 1) {
                this.warning = `${notFound.length} students not found: <ul class="mt-1 mb-0"><li>${_.join(notFound, '</li><li>')}</li></ul>`
              }
              resolve(validSids)
            })
          }
        } else {
          this.warning = 'Please provide one or more SIDs.'
          resolve(validSids)
        }
      })
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
