<script>
import _ from 'lodash'
import {mapActions, mapGetters} from 'vuex'

const $_flatten = categories => {
  let flattened = []
  _.each(categories, category => {
    flattened.push(category)
    _.each(_.concat(category.courseRequirements, category.subcategories), child => {
      flattened.push(child)
      if (child.courseRequirements) {
        flattened = _.concat(flattened, child.courseRequirements)
      }
    })
  })
  return flattened
}

const $_isValidUnits = (value, maxAllowed) => !isNaN(value) && value > 0 && value <= maxAllowed

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
      'assignCourseToCategory',
      'copyCourseAndAssign',
      'createCategory',
      'createUnitRequirement',
      'deleteCategory',
      'deleteCourse',
      'deleteUnitRequirement',
      'dismissAlert',
      'init',
      'onDrop',
      'onDragEnd',
      'onDragStart',
      'setDisableButtons',
      'setDraggingTarget',
      'setIncludeNotesWhenPrint',
      'updateCategory',
      'updateCourse',
      'updateNote',
      'updateUnitRequirement'
    ]),
    categoryHasCourse(category, course) {
      return _.map(category.courses, this.getCourseKey).includes(this.getCourseKey(course))
    },
    findCategoriesByTypes(types, position) {
      return _.filter($_flatten(this.categories), c => c.position === position && _.includes(types, c.categoryType))
    },
    findCategoryById(categoryId) {
      return categoryId ? _.find($_flatten(this.categories), ['id', categoryId]) : null
    },
    getCourse(courseId) {
      return _.find(this.courses.assigned.concat(this.courses.unassigned), ['id', courseId])
    },
    getCourseKey: course => course && `${course.termId}-${course.sectionId}`,
    getCourses(category) {
      if (this.courses) {
        const categoryCourseIds = _.map(category.courses, 'id')
        const predicate = c => _.includes(categoryCourseIds, c.id)
        const courses = _.filter(this.courses.assigned.concat(this.courses.unassigned), predicate)
        return courses.concat(category.courseRequirements)
      } else {
        return category.courseRequirements
      }
    },
    isValidUnits: $_isValidUnits,
    unitsWereEdited: course => {
      return !!_.get(course, 'units') && (course.units !== course.sis.units)
    },
    validateUnitRange(unitsLower, unitsUpper, maxAllowed) {
      const invalid = message => ({valid: false, message})
      if ($_isValidUnits(unitsLower, maxAllowed)) {
        if (_.isNil(unitsUpper)) {
          return {valid: true}
        } else {
          if ($_isValidUnits(unitsUpper, maxAllowed)) {
            const empty = _.isEmpty(unitsLower) && _.isEmpty(unitsUpper)
            return empty || parseFloat(unitsLower) <= parseFloat(unitsUpper) ? {valid: true} : invalid('Invalid range')
          } else {
            return invalid('Invalid upper range value')
          }
        }
      } else {
        return invalid(this.showUnitsUpperInput ? 'Invalid lower range value.' : 'Invalid')
      }
    }
  }
}
</script>
