<template>
  <div>
    <div v-if="student" class="border-bottom light-blue-background pb-2">
      <StudentProfileHeader
        :compact="true"
        :link-to-student-profile="true"
        :student="student"
      />
    </div>
    <Spinner />
    <div v-if="!loading">
      <div class="m-3 pt-2">
        <b-container class="px-0 mx-0" :fluid="true">
          <b-row>
            <b-col>
              <h1 id="page-header" class="page-section-header">Degree Check History</h1>
            </b-col>
            <b-col>
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
            </b-col>
          </b-row>
        </b-container>
      </div>
      <div v-if="degreeChecks.length" class="mx-3">
        <b-table-lite
          id="degree-checks-table"
          :fields="[
            {key: 'name', label: 'Degree Check', tdClass: 'align-middle', thClass: 'w-50'},
            {key: 'updatedAt', label: 'Last Updated', tdClass: 'align-top'},
            {key: 'updatedBy', label: 'Advisor'},
            {key: 'parentTemplateUpdatedAt', label: 'Template Last Updated', tdClass: 'align-top'}
          ]"
          :items="degreeChecks"
          borderless
          fixed
          stacked="md"
          thead-class="sortable-table-header text-nowrap"
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
            {{ DateTime.fromJSDate(row.item.updatedAt).toFormat('MMM D, YYYY') }}
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
        </b-table-lite>
      </div>
      <div v-if="!degreeChecks.length" class="pl-3">
        Student has no degree checks.
      </div>
    </div>
  </div>
</template>

<script setup>
import {mdiAlertRhombus} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import Spinner from '@/components/util/Spinner'
import StudentProfileHeader from '@/components/student/profile/StudentProfileHeader'
import Util from '@/mixins/Util'
import {getDegreeChecks} from '@/api/degree'
import {getStudentByUid} from '@/api/student'
import {DateTime} from 'luxon'

export default {
  name: 'StudentDegreeHistory',
  components: {Spinner, StudentProfileHeader},
  mixins: [Context, Util],
  data: () => ({
    degreeChecks: undefined,
    student: undefined
  }),
  created() {
    let uid = this._get(this.$route, 'params.uid')
    if (this.currentUser.inDemoMode) {
      // In demo-mode we do not want to expose UID in browser location bar.
      uid = window.atob(uid)
    }
    getStudentByUid(uid, true).then(data => {
      this.student = data
      getDegreeChecks(uid).then(data => {
        this.degreeChecks = data
        this._each(this.degreeChecks, degreeCheck => {
          if (degreeCheck.parentTemplateUpdatedAt) {
            degreeCheck.showRevisionIndicator = DateTime.fromJSDate(new Date(degreeCheck.createdAt)) < (new Date(degreeCheck.parentTemplateUpdatedAt))
          } else {
            degreeCheck.showRevisionIndicator = false
          }
        })
        const studentName = this.currentUser.inDemoMode ? 'Student' : this.student.name
        this.loadingComplete()
        this.alertScreenReader(`${studentName} Degree History`)
      })
    })
  }
}
</script>
