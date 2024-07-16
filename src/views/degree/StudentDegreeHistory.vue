<template>
  <div class="default-margins">
    <div v-if="student" class="border-bottom light-blue-background pb-2">
      <StudentProfileHeader
        :compact="true"
        :link-to-student-profile="true"
        :student="student"
      />
    </div>
    <div v-if="!loading">
      <div class="ma-3 pt-2">
        <v-container class="px-0 mx-0" :fluid="true">
          <v-row>
            <v-col>
              <h1 id="page-header" class="page-section-header">Degree Check History</h1>
            </v-col>
            <v-col>
              <div v-if="currentUser.canEditDegreeProgress" class="d-flex justify-content-end">
                <div class="pr-2">
                  <router-link
                    id="create-new-degree"
                    :to="`${studentRoutePath(student.uid, currentUser.inDemoMode)}/degree/create`"
                  >
                    Create New Degree
                  </router-link>
                </div>
              </div>
            </v-col>
          </v-row>
        </v-container>
      </div>
      <div v-if="degreeChecks.length" class="mx-3">
        <!--
        TODO:
        tdClass
        thClass
        borderless
        fixed
        stacked
        thead-class
        -->
        <v-data-table
          id="degree-checks-table"
          :fields="[
            {key: 'name', title: 'Degree Check', tdClass: 'align-middle', thClass: 'w-50'},
            {key: 'updatedAt', title: 'Last Updated', tdClass: 'align-top'},
            {key: 'updatedBy', title: 'Advisor'},
            {key: 'parentTemplateUpdatedAt', title: 'Template Last Updated', tdClass: 'align-top'}
          ]"
          :items="degreeChecks"
          borderless
          fixed
          stacked="md"
          thead-class="text-no-wrap"
        >
          <template #cell(name)="row">
            <router-link
              :id="`degree-check-${row.item.id}-link`"
              :to="`/student/degree/${row.item.id}`"
              v-html="`${row.item.name}`"
            />
            <span v-if="row.item.isCurrent" class="ml-2">(current)</span>
          </template>
          <template #cell(updatedAt)="row">
            {{ DateTime.fromJSDate(row.item.updatedAt).toFormat('MMM D, yyyy') }}
          </template>
          <template #cell(updatedBy)="row">
            <div class="align-right w-100">
              {{ row.item.updatedByName || '&mdash;' }}
            </div>
          </template>
          <template #cell(parentTemplateUpdatedAt)="row">
            <v-icon
              v-if="row.item.showRevisionIndicator"
              class="boac-exclamation mr-1"
              :icon="mdiAlertRhombus"
              :title="`Revisions to the original degree template have been made since the creation of this degree check.`"
            />
            <span v-if="row.item.parentTemplateUpdatedAt" :class="{'boac-exclamation': row.item.showRevisionIndicator}">{{ DateTime.fromJSDate(row.item.parentTemplateUpdatedAt).toFormat('MMM D, YYYY') }}</span>
            <span v-if="!row.item.parentTemplateUpdatedAt">&mdash;</span>
            <div class="sr-only">
              Note: Revisions to the original degree template have been made since the creation of this degree check.
            </div>
          </template>
        </v-data-table>
      </div>
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
import {mdiAlertRhombus} from '@mdi/js'
import {useContextStore} from '@/stores/context'
import {computed, onMounted, ref} from 'vue'
import {each, get} from 'lodash'

const contextStore = useContextStore()
const currentUser = contextStore.currentUser

const degreeChecks = ref(undefined)
const loading = computed(() => contextStore.loading)
const student = ref(undefined)

contextStore.loadingStart()

onMounted(() => {
  let uid = get(this.$route, 'params.uid')
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
