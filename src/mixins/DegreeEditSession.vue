<script>
import _ from 'lodash'
import {mapActions, mapGetters} from 'vuex'

const $_flatten = categories => {
  let flattened = []
  _.each(categories, category => {
    flattened.push(category)
    _.each(_.concat(category.courses, category.subcategories), child => {
      flattened.push(child)
      flattened = _.concat(flattened, child.courses)
    })
  })
  return flattened
}

export default {
  name: 'DegreeEditSession',
  computed: {
    ...mapGetters('degreeEditSession', [
      'categories',
      'degreeEditSessionToString',
      'degreeName',
      'disableButtons',
      'editMode',
      'templateId',
      'unitRequirements'
    ])
  },
  methods: {
    ...mapActions('degreeEditSession', [
      'createCategory',
      'createUnitRequirement',
      'deleteCategory',
      'init',
      'loadTemplate',
      'setDisableButtons',
      'setEditMode',
      'updateCategory',
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
