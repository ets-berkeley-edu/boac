<template>
  <div>
    <div v-if="student" class="border-bottom bg-sky-blue pb-2">
      <StudentProfileHeader
        :compact="true"
        :link-to-student-profile="true"
        :student="student"
      />
    </div>
    <div v-if="!loading" class="default-margins">
      <div class="align-center d-flex justify-space-between">
        <h1 id="page-header" class="page-section-header">Degree Check History</h1>
        <div v-if="currentUser.canEditDegreeProgress" class="mr-2">
          <router-link id="create-new-degree" :to="`${studentRoutePath(student.uid, currentUser.inDemoMode)}/degree/create`">
            Create New Degree
          </router-link>
        </div>
      </div>
      <v-data-table
        v-if="degreeChecks.length"
        id="degree-checks-table"
        :cell-props="data => {
          const bgColor = data.index % 2 === 0 ? 'bg-grey-lighten-4' : ''
          return {
            class: `${bgColor} font-size-16`,
            id: `td-degree-check-${data.item.id}-column-${data.column.key}`,
            style: $vuetify.display.mdAndUp ? 'max-width: 200px;' : ''
          }
        }"
        class="mt-3"
        density="comfortable"
        :headers="[
          {key: 'name', headerProps: {class: 'degree-history-column-header w-50'}, title: 'Degree Check', thClass: 'w-50'},
          {key: 'updatedAt', headerProps: {class: 'degree-history-column-header'}, title: 'Last Updated'},
          {key: 'updatedBy', headerProps: {class: 'degree-history-column-header'}, title: 'Advisor'},
          {key: 'parentTemplateUpdatedAt', headerProps: {class: 'degree-history-column-header'}, title: 'Template Last Updated'}
        ]"
        :header-props="{class: 'font-weight-bold text-no-wrap'}"
        hide-default-footer
        disable-sort
        :items="degreeChecks"
        :items-per-page="-1"
        :row-props="data => ({
          id: `tr-degree-check-${data.item.id}`
        })"
      >
        <template #item.name="{item}">
          <router-link
            :id="`degree-check-${item.id}-link`"
            :to="`/student/degree/${item.id}`"
            v-html="`${item.name}`"
          />
          <span v-if="item.isCurrent" class="ml-2">(current)</span>
        </template>
        <template #item.updatedAt="{item}">
          {{ DateTime.fromISO(item.updatedAt).toFormat('DD') }}
        </template>
        <template #item.updatedBy="{item}">
          <div class="align-right w-100">
            {{ item.updatedByName || '&mdash;' }}
          </div>
        </template>
        <template #item.parentTemplateUpdatedAt="{item}">
          <v-icon
            v-if="true || item.showRevisionIndicator"
            class="warning mr-2"
            :icon="mdiAlert"
            size="18"
            title="Revisions to the original degree template have been made since the creation of this degree check."
          />
          <span
            v-if="item.parentTemplateUpdatedAt"
            :class="{'warning': true || item.showRevisionIndicator}"
          >
            {{ DateTime.fromISO(item.parentTemplateUpdatedAt).toFormat('DD') }}
          </span>
          <span v-if="!item.parentTemplateUpdatedAt">&mdash;</span>
          <div class="sr-only">
            Note: Revisions to the original degree template have been made since the creation of this degree check.
          </div>
        </template>
      </v-data-table>
      <div v-if="!degreeChecks.length" class="pl-3">
        Student has no degree checks.
      </div>
    </div>
  </div>
</template>

<script setup>
import StudentProfileHeader from '@/components/student/profile/StudentProfileHeader'
import {alertScreenReader, studentRoutePath} from '@/lib/utils'
import {DateTime} from 'luxon'
import {getDegreeChecks} from '@/api/degree'
import {getStudentByUid} from '@/api/student'
import {mdiAlert} from '@mdi/js'
import {useContextStore} from '@/stores/context'
import {computed, onMounted, ref} from 'vue'
import {each} from 'lodash'
import {useRoute} from 'vue-router'

const contextStore = useContextStore()
const currentUser = contextStore.currentUser

const degreeChecks = ref(undefined)
const loading = computed(() => contextStore.loading)
const student = ref(undefined)

contextStore.loadingStart()

onMounted(() => {
  let uid = useRoute().params.uid
  if (currentUser.inDemoMode) {
    // In demo-mode we do not want to expose UID in browser location bar.
    uid = window.atob(uid)
  }
  getStudentByUid(uid, true).then(data => {
    student.value = data
    getDegreeChecks(uid).then(data => {
      degreeChecks.value = data
      each(degreeChecks.value, degreeCheck => {
        if (degreeCheck.parentTemplateUpdatedAt) {
          const parentTemplateUpdatedAt = new Date(degreeChecks.value.parentTemplateUpdatedAt)
          const createdAt = new Date(degreeChecks.value.createdAt)
          degreeCheck.showRevisionIndicator = createdAt < parentTemplateUpdatedAt
        } else {
          degreeCheck.showRevisionIndicator = false
        }
      })
      const studentName = currentUser.inDemoMode ? 'Student' : student.value.name
      contextStore.loadingComplete()
      alertScreenReader(`${studentName} Degree History`)
    })
  })
})
</script>

<style>
.degree-history-column-header {
  color: #666;
  font-weight: 700 !important;
  height: 30px !important;
}
</style>
