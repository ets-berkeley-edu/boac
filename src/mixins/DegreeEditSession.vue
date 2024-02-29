<script>
import {mapActions, mapState} from 'pinia'
import {useDegreeProgressStore} from '@/stores/degree-edit-session'

export default {
  name: 'DegreeEditSession',
  computed: {
    ...mapState(useDegreeProgressStore, [
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
    ...mapActions(useDegreeProgressStore, [
      'dismissAlert',
      'draggingContextReset',
      'setDisableButtons',
      'setDraggingTarget',
      'setIncludeNotesWhenPrint',
    ]),
    onDragStart: (course, dragContext) => useDegreeProgressStore().dragStart(course, dragContext)
  }
}
</script>
