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
      'createCategory',
      'createUnitRequirement',
      'deleteCategory',
      'deleteUnitRequirement',
      'init',
      'setDisableButtons',
      'updateCategory',
      'updateNote',
      'updateUnitRequirement'
    ]),
    findCategoriesByTypes(types, position) {
      return this.$_.filter($_flatten(this.categories), c => c.position === position && _.includes(types, c.categoryType))
    },
    findCategoryById(categoryId) {
      return categoryId ? _.find($_flatten(this.categories), ['id', categoryId]) : null
    },
    getCourse(courseId) {
      return _.find(this.courses.assigned.concat(this.courses.unassigned), ['id', courseId])
    },
    getCourses(category) {
      return _.filter(this.courses.assigned.concat(this.courses.unassigned), c => _.includes(category.courseIds, c.id))
    },
    isTransientCategory(category) {
      return category.position === -1
    }
  }
}
</script>
