<script>
import {mapGetters} from 'vuex'
import Berkeley from '@/mixins/Berkeley'

export default {
  name: 'CurrentUserExtras',
  mixins: [Berkeley],
  computed: {
    ...mapGetters('currentUserExtras', [
      'includeAdmits',
      'myAdmitCohorts',
      'myCohorts',
      'myCuratedGroups',
      'preferences'
    ])
  },
  methods: {
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
