<script>
import _ from 'lodash'
import {mapActions, mapGetters} from 'vuex'

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
      'updateUnitRequirement'
    ]),
    findCategoriesByTypes(types, position) {
      let flattened = []
      _.each(this.categories, category => {
        flattened.push(category)
        _.each(category.children, subcategory => {
          flattened.push(subcategory)
          flattened = flattened.concat(subcategory.children)
        })
      })
      return this.$_.filter(flattened, c => c.position === position && _.includes(types, c.categoryType))
    }
  }
}
</script>
