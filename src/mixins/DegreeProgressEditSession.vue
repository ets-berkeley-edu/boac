<script>
import {mapActions, mapGetters} from 'vuex'

export default {
  name: 'DegreeProgressEditSession',
  computed: {
    ...mapGetters('degreeProgressEditSession', [
      'degreeName',
      'templateId',
      'unitRequirements'
    ])
  },
  methods: {
    ...mapActions('degreeProgressEditSession', [
      'addUnitRequirement',
      'init',
      'loadTemplate',
      'saveUnitRequirements'
    ])
  }
}
</script>
