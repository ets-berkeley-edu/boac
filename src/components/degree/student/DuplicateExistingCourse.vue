<template>
  <div>
    <div v-if="isMenuOpen" class="my-2">
      <div class="font-size-16 font-weight-medium text-surface-variant">
        Duplicate Course
      </div>
      <div class="my-2">
        <select
          id="add-course-select"
          v-model="selected"
          class="select-menu w-100"
          :disabled="isSaving || !options.length"
        >
          <option
            id="add-course-select-option-null"
            :value="null"
            @click="onSelect"
          >
            Choose...
          </option>
          <option
            v-for="option in options"
            :id="`add-course-select-option-${option.id}`"
            :key="option.id"
            :value="option"
            @click="onSelect"
          >
            {{ option.name }}
          </option>
        </select>
      </div>
      <div class="d-flex mt-2">
        <ProgressButton
          id="add-course-save-btn"
          :action="onClickSave"
          color="primary"
          :disabled="isSaving || !selected"
          :in-progress="isSaving"
          :text="isSaving ? 'Saving' : 'Save'"
        />
        <v-btn
          id="add-course-cancel-btn"
          :disabled="isSaving"
          variant="text"
          @click="cancel"
        >
          Cancel
        </v-btn>
      </div>
    </div>
    <div v-if="!isMenuOpen">
      <span v-if="!options.length" aria-live="polite" class="sr-only">No courses available to copy.</span>
      <v-btn
        v-if="currentUser.canEditDegreeProgress"
        id="duplicate-existing-course"
        class="align-center d-flex flex-row-reverse font-size-16 pl-0 text-no-wrap"
        color="primary"
        :disabled="degreeStore.disableButtons || !options.length"
        variant="text"
        @click.prevent="openMenu"
      >
        <v-icon :icon="mdiPlus" size="20" />
        Duplicate Course
      </v-btn>
    </div>
  </div>
</template>

<script setup>
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {copyCourse} from '@/api/degree'
import {mdiPlus} from '@mdi/js'
import {refreshDegreeTemplate} from '@/stores/degree-edit-session/utils'
import {computed, ref} from 'vue'
import {filter as _filter, sortBy} from 'lodash'
import {useContextStore} from '@/stores/context'
import {useDegreeStore} from '@/stores/degree-edit-session/index'
import ProgressButton from '@/components/util/ProgressButton.vue'

const contextStore = useContextStore()
const degreeStore = useDegreeStore()

const currentUser = contextStore.currentUser
const isMenuOpen = ref(false)
const isSaving = ref(false)
const selected = ref(null)
const options = computed(() => {
  const courses = degreeStore.courses.assigned.concat(degreeStore.courses.unassigned)
  return _filter(sortBy(courses, [c => c.name.toLowerCase()], ['name', 'id']), c => !c.isCopy)
})

const cancel = () => {
  isMenuOpen.value = isSaving.value = false
  degreeStore.setDisableButtons(false)
  alertScreenReader('Canceled')
  putFocusNextTick('duplicate-existing-course')
}

const onClickSave = () => {
  isSaving.value = true
  alertScreenReader('Saving')
  copyCourse(selected.value.id).then(course => {
    refreshDegreeTemplate(degreeStore.templateId).then(() => {
      isMenuOpen.value = isSaving.value = false
      selected.value = null
      degreeStore.setDisableButtons(false)
      alertScreenReader('Course duplicated and put in the list of Unassigned.')
      putFocusNextTick(`assign-course-${course.id}-menu-container`, 'button')
    })
  })
}

const onSelect = () => {
  alertScreenReader(selected.value ? `${selected.value.name} selected` : 'Selection set to null.')
}

const openMenu = () => {
  degreeStore.setDisableButtons(true)
  isMenuOpen.value = true
  alertScreenReader('The \'Duplicate Course\' menu is open.')
  putFocusNextTick('add-course-select')
}
</script>
