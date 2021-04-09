<script>
import {mapActions, mapGetters} from 'vuex'

export default {
  name: 'DegreeEditSession',
  computed: {
    ...mapGetters('degreeEditSession', [
      'degreeName',
      'editMode',
      'templateId',
      'unitRequirements'
    ])
  },
  methods: {
    ...mapActions('degreeEditSession', [
      'createUnitRequirement',
      'updateUnitRequirement',
      'init',
      'loadTemplate',
      'setEditMode'
    ])
  }
}
</script>
