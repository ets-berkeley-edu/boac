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
      'init',
      'loadTemplate',
      'setEditMode'
    ])
  }
}
</script>
