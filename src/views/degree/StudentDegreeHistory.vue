<template>
  <div>
    <Spinner />
    <div v-if="!loading">
      <div class="border-bottom light-blue-background pb-2">
        <StudentProfileHeader
          :compact="true"
          :link-to-student-profile="true"
          :student="student"
        />
      </div>
      <div class="m-3 pt-2">
        <b-container class="px-0 mx-0" :fluid="true">
          <b-row>
            <b-col>
              <h1 id="page-header" class="page-section-header">Degree Check History</h1>
            </b-col>
            <b-col>
              <div class="d-flex justify-content-end">
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
      <div v-if="student.degreeChecks.length">
        <b-table-lite
          id="degree-checks-table"
          :fields="[
            {key: 'name', label: 'Degree Check', tdClass: 'align-middle', thClass: 'w-50'},
            {key: 'updatedAt', label: 'Last Updated', tdClass: 'align-top'},
            {key: 'updatedBy', label: 'Advisor'}
          ]"
          :items="student.degreeChecks"
          borderless
          fixed
          stacked="md"
          thead-class="sortable-table-header text-nowrap"
        >
          <template #cell(name)="row">
            <router-link
              :id="`degree-check-${row.item.id}-link`"
              :to="`/student/${student.uid}/degree/${row.item.id}`"
              v-html="`${row.item.name}`"
            />
            <span v-if="row.item.isCurrent" class="ml-2">(current)</span>
          </template>
          <template #cell(updatedAt)="row">
            {{ row.item.updatedAt | moment('MMM D, YYYY') }}
          </template>
          <template #cell(updatedBy)="row">
            <div class="align-right w-100">
              {{ advisorNamesByUid[row.item.updatedBy] }}
            </div>
          </template>
        </b-table-lite>
      </div>
      <div v-if="!student.degreeChecks.length" class="p-5">
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
import {getCalnetProfileByUid} from '@/api/user'
import {getStudentByUid} from '@/api/student'

export default {
  name: 'StudentDegreeHistory',
  components: {Spinner, StudentProfileHeader},
  mixins: [Context, Loading, Util],
  data: () => ({
    advisorNamesByUid: undefined
  }),
  created() {
    const uid = this.$_.get(this.$route, 'params.uid')
    getStudentByUid(uid).then(data => {
      this.student = data
      this.fetchAdvisors().then(() => {
        const studentName = this.$currentUser.inDemoMode ? 'Student' : this.student.name
        this.loaded(`${studentName} Degree History`)
      })
    })
  },
  methods: {
    fetchAdvisors() {
      this.advisorNamesByUid = {}
      return new Promise(resolve => {
        const uniqueUids = this.$_.uniq(this.$_.map(this.student.degreeChecks, 'updatedBy'))
        this.$_.each(uniqueUids, uid => {
          getCalnetProfileByUid(uid).then(data => {
            this.advisorNamesByUid[uid] = data.name || `${data.uid} (UID)`
            if (uid === this.$_.last(uniqueUids)) {
              resolve()
            }
          })
        })
      })
    }
  }
}
</script>
