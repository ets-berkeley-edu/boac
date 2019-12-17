<script>
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'UserMetadata',
  computed: {
    ...mapGetters('user', [
      'preferences',
      'user'
    ]),
    ...mapGetters('cohort', ['myCohorts']),
    ...mapGetters('curated', ['myCuratedGroups']),
    ...mapGetters('note', [
      'noteTemplates',
      'suggestedNoteTopics'
    ])
  },
  methods: {
    ...mapActions('user', [
      'gaAppointmentEvent',
      'gaCohortEvent',
      'gaCourseEvent',
      'gaCuratedEvent',
      'gaNoteEvent',
      'gaSearchEvent',
      'gaStudentAlert',
      'setUserPreference'
    ])
  }
};
</script>
