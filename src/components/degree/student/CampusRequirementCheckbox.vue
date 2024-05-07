<template>
  <div class="d-flex justify-content-center">
    <b-form-checkbox
      :id="`column-${position}-${campusRequirement.key}-satisfy-checkbox`"
      v-model="isSatisfied"
      :disabled="disableButtons || !canEdit"
      :button="!canEdit"
      button-variant="outline-transparent"
      @change="toggle"
    >
      <v-icon
        v-if="!canEdit"
        :icon="isSatisfied ? mdiCheckboxMarkedOutline : mdiSquareOutline"
        class="disabled-checkbox"
        :class="{'fully-opaque': printable}"
      />
      <span class="sr-only">{{ campusRequirement.name }} is {{ isSatisfied ? 'satisfied' : 'unsatisfied' }}</span>
    </b-form-checkbox>
  </div>
</template>

<script setup>
import {mdiCheckboxMarkedOutline, mdiSquareOutline} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import Util from '@/mixins/Util'
import {alertScreenReader} from '@/lib/utils'
import {refreshDegreeTemplate} from '@/stores/degree-edit-session/utils'
import {toggleCampusRequirement} from '@/api/degree'

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
    this.canEdit = this.currentUser.canEditDegreeProgress && !this.printable
    this.isSatisfied = this.campusRequirement.category.categoryType === 'Campus Requirement, Satisfied'
  },
  methods: {
    toggle() {
      this.setDisableButtons(true)
      toggleCampusRequirement(this.campusRequirement.category.id, this.isSatisfied).then(() => {
        refreshDegreeTemplate(this.templateId)
        alertScreenReader(`${this.campusRequirement.name} requirement ${this.isSatisfied ? 'satisfied' : 'unsatisfied'}`)
        this.putFocusNextTick(`column-${this.position}-${this.campusRequirement.key}-satisfy-checkbox`)
        this.setDisableButtons(false)
      })
    }
  }
}
</script>

<style scoped>
.disabled-checkbox {
  color: #000;
  color-adjust: exact;
}
</style>
