<template>
  <div class="d-flex justify-content-center">
    <b-form-checkbox
      :id="`column-${position}-${campusRequirement.key}-satisfy-checkbox`"
      v-model="isSatisfied"
      :disabled="disableButtons || !canEdit"
      :plain="!canEdit"
      @change="toggle"
    >
      <span class="sr-only">{{ campusRequirement.name }} is {{ isSatisfied ? 'satisfied' : 'unsatisfied' }}</span>
    </b-form-checkbox>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import Util from '@/mixins/Util'

export default {
  name: 'CampusRequirementCheckbox',
  mixins: [Context, DegreeEditSession, Util],
  props: {
    campusRequirement: {
      required: true,
      type: Object
    },
    position: {
      required: true,
      type: Number
    },
    printable: {
      required: true,
      type: Boolean
    }
  },
  data: () => ({
    canEdit: undefined,
    isSatisfied: undefined
  }),
  created() {
    this.canEdit = this.$currentUser.canEditDegreeProgress && !this.printable
    this.isSatisfied = this.campusRequirement.category.categoryType === 'Campus Requirement, Satisfied'
  },
  methods: {
    toggle() {
      this.setDisableButtons(true)
      this.toggleCampusRequirement({
        categoryId: this.campusRequirement.category.id,
        isSatisfied: this.isSatisfied
      }).then(() => {
        this.$announcer.polite(`${this.campusRequirement.name} requirement ${this.isSatisfied ? 'satisfied' : 'unsatisfied'}`)
        this.$putFocusNextTick(`column-${this.position}-${this.campusRequirement.key}-satisfy-checkbox`)
        this.setDisableButtons(false)
      })
    }
  }
}
</script>
