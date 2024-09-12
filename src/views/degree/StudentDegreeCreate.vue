<template>
  <div v-if="!loading">
    <div class="border-bottom bg-sky-blue pb-2">
      <StudentProfileHeader :compact="true" :link-to-student-profile="true" :student="student" />
    </div>
    <div class="default-margins">
      <h2 class="page-section-header">Create <span :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ student.firstName }}</span>'s Degree Check</h2>
      <div>
        Choose a new degree check for <span :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ student.name }}</span> from the list of options in the menu below.
      </div>
      <div class="mt-3">
        <h3 class="font-size-18 font-weight-bold">Add Degree Check</h3>
      </div>
      <div v-if="templates.length">
        <div class="my-2 w-30">
          <select
            id="degree-template-select"
            v-model="selectedOption"
            aria-label="Select a degree template"
            class="select-menu select-menu-max-width"
            :disabled="isSaving"
          >
            <option
              id="degree-check-select-option-null"
              :value="null"
            >
              Choose...
            </option>
            <option
              v-for="option in templates"
              :id="`degree-check-select-option-${option.id}`"
              :key="option.id"
              class="truncate-with-ellipsis"
              :title="option.name"
              :value="option"
            >
              {{ option.name }}
            </option>
          </select>
        </div>
        <div class="align-center d-flex mt-6">
          <div class="mr-1">
            <ProgressButton
              id="save-degree-check-btn"
              :action="onClickSave"
              :disabled="isSaving || !selectedOption"
              :in-progress="isSaving"
              :text="isSaving ? 'Saving' : 'Save Degree Check'"
            />
            <v-btn
              id="cancel-create-degree-check-btn"
              color="primary"
              :disabled="isSaving"
              variant="text"
              @click="cancel"
            >
              Cancel
            </v-btn>
          </div>
        </div>
      </div>
      <div v-if="!templates.length">
        No templates available.
        You can <router-link id="create-filtered-cohort" to="/degrees">create a Degree Check</router-link> and then
        return to this page to proceed.
      </div>
    </div>
  </div>
</template>

<script setup>
import ProgressButton from '@/components/util/ProgressButton.vue'
import router from '@/router'
import StudentProfileHeader from '@/components/student/profile/StudentProfileHeader'
import {alertScreenReader, putFocusNextTick, setPageTitle, studentRoutePath} from '@/lib/utils'
import {computed, onMounted, ref, watch} from 'vue'
import {createDegreeCheck, getDegreeTemplates} from '@/api/degree'
import {getStudentByUid} from '@/api/student'
import {useContextStore} from '@/stores/context'
import {useRoute} from 'vue-router'

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const isSaving = ref(false)
const loading = computed(() => contextStore.loading)
const selectedOption = ref(null)
const student = ref(undefined)
const templates = ref(undefined)

watch(selectedOption, () => {
  if (selectedOption.value) {
    alertScreenReader(`${selectedOption.value.name} selected`)
    putFocusNextTick('save-degree-check-btn')
  }
})

contextStore.loadingStart()

onMounted(() => {
  let uid = useRoute().params.uid
  if (currentUser.inDemoMode) {
    // In demo-mode we do not want to expose UID in browser location bar.
    uid = window.atob(uid)
  }
  getStudentByUid(uid, true).then(data => {
    student.value = data
    setPageTitle(currentUser.inDemoMode ? 'Student' : student.value.name)
    getDegreeTemplates().then(data => {
      templates.value = data
      contextStore.loadingComplete()
      alertScreenReader(`Add Degree Check for ${student.value.name}`)
    })
  })
})

const cancel = () => {
  alertScreenReader('Canceled')
  router.push(studentRoutePath(student.value.uid, currentUser.inDemoMode))
}

const onClickSave = () => {
  isSaving.value = true
  alertScreenReader('Saving')
  createDegreeCheck(student.value.sid, selectedOption.value.id).then(data => {
    router.push(`/student/degree/${data.id}`).then(() => {
      isSaving.value = false
    })
  })
}
</script>

<style scoped>
.select-menu-max-width {
  max-width: 75%;
}
</style>
