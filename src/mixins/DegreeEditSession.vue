<script>
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
    findCategoriesByType(type, position) {
      return this.$_.filter(this.categories, c => c.position === position && c.categoryType === type)
    }
  }
}
</script>
