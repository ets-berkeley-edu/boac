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
              <div v-if="$currentUser.canEditDegreeProgress" class="d-flex justify-content-end">
                <div class="pr-2">
                  <router-link
                    id="create-new-degree"
                    :to="`/student/${student.uid}/degree/create`"
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
            {key: 'updatedBy', label: 'Advisor'}
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
            {{ row.item.updatedAt | moment('MMM D, YYYY') }}
          </template>
          <template #cell(updatedBy)="row">
            <div class="align-right w-100">
              {{ advisorNamesById[row.item.updatedBy] }}
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

<script>
import Context from '@/mixins/Context'
import Loading from '@/mixins/Loading'
import Spinner from '@/components/util/Spinner'
import StudentProfileHeader from '@/components/student/profile/StudentProfileHeader'
import Util from '@/mixins/Util'
import {getCalnetProfileByUserId} from '@/api/user'
import {getDegreeChecks} from '@/api/degree'
import {getStudentByUid} from '@/api/student'

export default {
  name: 'StudentDegreeHistory',
  components: {Spinner, StudentProfileHeader},
  mixins: [Context, Loading, Util],
  data: () => ({
    advisorNamesById: undefined,
    degreeChecks: undefined,
    student: undefined
  }),
  created() {
    const uid = this.$_.get(this.$route, 'params.uid')
    getStudentByUid(uid, true).then(data => {
      this.student = data
      const done = () => {
        const studentName = this.$currentUser.inDemoMode ? 'Student' : this.student.name
        this.loaded(`${studentName} Degree History`)
      }
      this.advisorNamesById = {}
      getDegreeChecks(uid).then(data => {
        this.degreeChecks = data
        const uniqueUserIds = this.$_.uniq(this.$_.map(data, 'updatedBy'))
        if (uniqueUserIds.length) {
          this.$_.each(uniqueUserIds, userId => {
            getCalnetProfileByUserId(userId).then(data => {
              this.advisorNamesById[userId] = data.name || `${data.uid} (UID)`
              if (userId === this.$_.last(uniqueUserIds)) {
                done()
              }
            })
          })
        } else {
          done()
        }
      })
    })
  }
}
</script>
