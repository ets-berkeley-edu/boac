<template>
  <div class="d-flex justify-content-center">
    <v-checkbox
      :id="`column-${position}-${campusRequirement.key}-satisfy-checkbox`"
      v-model="isSatisfied"
      :disabled="degreeStore.disableButtons || !canEdit"
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
    </v-checkbox>
  </div>
</template>

<script setup>
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {mdiCheckboxMarkedOutline, mdiSquareOutline} from '@mdi/js'
import {refreshDegreeTemplate} from '@/stores/degree-edit-session/utils'
import {toggleCampusRequirement} from '@/api/degree'
import {useContextStore} from '@/stores/context'
import {useDegreeStore} from '@/stores/degree-edit-session/index'


const props = defineProps({
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
})

const contextStore = useContextStore()
const degreeStore = useDegreeStore()

const currentUser = contextStore.currentUser
const canEdit = currentUser.canEditDegreeProgress && !props.printable
const isSatisfied = props.campusRequirement.category.categoryType === 'Campus Requirement, Satisfied'

const toggle = () => {
  degreeStore.setDisableButtons(true)
  toggleCampusRequirement(props.campusRequirement.category.id, isSatisfied).then(() => {
    refreshDegreeTemplate(degreeStore.templateId)
    alertScreenReader(`${props.campusRequirement.name} requirement ${isSatisfied ? 'satisfied' : 'unsatisfied'}`)
    putFocusNextTick(`column-${props.position}-${props.campusRequirement.key}-satisfy-checkbox`)
    degreeStore.setDisableButtons(false)
  })
}
</script>

<style scoped>
.disabled-checkbox {
  color: #000;
  color-adjust: exact;
}
</style>
