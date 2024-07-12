<script>
import {mapActions, mapState} from 'pinia'
import {useDegreeStore} from '@/stores/degree-edit-session'

export default {
  name: 'DegreeEditSession',
  computed: {
    ...mapState(useDegreeStore, [
      'addCourseMenuOptions',
      'categories',
      'courses',
      'createdAt',
      'createdBy',
      'degreeEditSessionToString',
      'degreeName',
      'degreeNote',
      'disableButtons',
      'dismissedAlerts',
      'draggingContext',
      'includeNotesWhenPrint',
      'isUserDragging',
      'lastPageRefreshAt',
      'parentTemplateId',
      'parentTemplateUpdatedAt',
      'sid',
      'templateId',
      'unitRequirements',
      'updatedAt',
      'updatedBy'
    ])
  },
  methods: {
    ...mapActions(useDegreeStore, [
      'dismissAlert',
      'draggingContextReset',
      'setDisableButtons',
      'setDraggingTarget',
      'setIncludeNotesWhenPrint',
    ]),
    onDragStart: (course, dragContext) => useDegreeStore().dragStart(course, dragContext)
  }
}
</script>
