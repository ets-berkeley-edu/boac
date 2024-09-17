<template>
  <div>
    <v-checkbox
      v-if="canEdit"
      :id="`column-${position}-${campusRequirement.key}-satisfy-checkbox`"
      v-model="isSatisfied"
      :aria-label="`${campusRequirement.name} is ${isSatisfied ? 'satisfied' : 'unsatisfied'}`"
      color="primary"
      density="compact"
      :disabled="degreeStore.disableButtons"
      hide-details
      @change="toggle"
    />
    <v-icon
      v-if="!canEdit"
      :icon="isSatisfied ? mdiCheckBold : mdiCloseThick"
      disabled
      :color="printable ? 'surface-variants' : (isSatisfied ? 'success' : 'error')"
      size="20"
    />
  </div>
</template>

<script setup>
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {mdiCheckBold, mdiCloseThick} from '@mdi/js'
import {refreshDegreeTemplate} from '@/stores/degree-edit-session/utils'
import {toggleCampusRequirement} from '@/api/degree'
import {useContextStore} from '@/stores/context'
import {useDegreeStore} from '@/stores/degree-edit-session/index'
import {ref} from 'vue'

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
const isSatisfied = ref(props.campusRequirement.category.categoryType === 'Campus Requirement, Satisfied')

const toggle = () => {
  toggleCampusRequirement(props.campusRequirement.category.id, isSatisfied.value).then(() => {
    refreshDegreeTemplate(degreeStore.templateId)
    alertScreenReader(`${props.campusRequirement.name} requirement ${isSatisfied.value ? 'satisfied' : 'unsatisfied'}`)
    putFocusNextTick(`column-${props.position}-${props.campusRequirement.key}-satisfy-checkbox`)
  })
}
</script>
