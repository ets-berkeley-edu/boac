<script>
import {mapActions, mapGetters} from 'vuex'

export default {
  name: 'DegreeEditSession',
  computed: {
    ...mapGetters('degreeEditSession', [
      'degreeName',
      'templateId',
      'unitRequirements'
    ])
  },
  methods: {
    ...mapActions('degreeEditSession', [
      'addUnitRequirement',
      'init',
      'loadTemplate',
      'saveUnitRequirements'
    ])
  }
}
</script>
