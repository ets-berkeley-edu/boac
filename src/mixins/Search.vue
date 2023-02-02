<script>
import {mapActions, mapGetters} from 'vuex'

export default {
  name: 'Search',
  computed: {
    ...mapGetters('search', [
      'domain',
      'includeAdmits',
      'includeCourses',
      'includeNotes',
      'includeStudents',
      'queryText',
      'topicOptions'
    ])
  },
  methods: {
    ...mapActions('search', [
      'init',
      'resetAdvancedSearch',
      'setIncludeAdmits',
      'setIncludeCourses',
      'setIncludeNotes',
      'setIncludeStudents',
      'setQueryText',
    ])
  }
}
</script>
