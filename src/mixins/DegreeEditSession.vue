<script>
import _ from 'lodash'
import {mapActions, mapGetters} from 'vuex'

const $_flatten = categories => {
  let flattened = []
  _.each(categories, category => {
    flattened.push(category)
    _.each(_.concat(category.courses, category.subcategories), child => {
      flattened.push(child)
      if (child.courses) {
        flattened = _.concat(flattened, child.courses)
      }
    })
  })
  return flattened
}

export default {
  name: 'DegreeEditSession',
  computed: {
    ...mapGetters('degreeEditSession', [
      'categories',
      'createdAt',
      'createdBy',
      'degreeEditSessionToString',
      'degreeName',
      'disableButtons',
      'editMode',
      'note',
      'templateId',
      'unassignedCourses',
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
      'loadTemplate',
      'refreshUnassignedCourses',
      'setDisableButtons',
      'setEditMode',
      'updateCategory',
      'updateNote',
      'updateUnitRequirement'
    ]),
    findCategoriesByTypes(types, position) {
      return this.$_.filter($_flatten(this.categories), c => c.position === position && _.includes(types, c.categoryType))
    },
    findCategoryById(categoryId) {
      return categoryId ? _.find($_flatten(this.categories), ['id', categoryId]) : null
    }
  }
}
</script>
