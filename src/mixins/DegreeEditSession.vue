<script>
import {mapGetters, mapMutations} from 'vuex'
import store from '@/store'

export default {
  name: 'DegreeEditSession',
  computed: {
    ...mapGetters('degree', [
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
    ...mapMutations('degree', [
      'dismissAlert',
      'draggingContextReset',
      'setDisableButtons',
      'setDraggingTarget',
      'setIncludeNotesWhenPrint',
    ]),
    onDragStart: (course, dragContext) => store.commit('degree/dragStart', {course, dragContext})
  }
}
</script>
