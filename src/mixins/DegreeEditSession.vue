<script>
import {mapActions, mapGetters} from 'vuex'

export default {
  name: 'DegreeEditSession',
  computed: {
    ...mapGetters('degreeEditSession', [
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
    ...mapActions('degreeEditSession', [
      'copyCourse',
      'createCategory',
      'createCourse',
      'createUnitRequirement',
      'deleteCategory',
      'deleteCourse',
      'deleteUnitRequirement',
      'dismissAlert',
      'onDrop',
      'onDragEnd',
      'onDragStart',
      'setDisableButtons',
      'setDraggingTarget',
      'setIncludeNotesWhenPrint',
      'updateCategory',
      'updateCourse',
      'updateCourseRequirement',
      'updateNote',
      'updateUnitRequirement'
    ])
  }
}
</script>
