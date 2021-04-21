<template>
  <b-container id="student-degree-check-header" class="px-0 mx-0" :fluid="true">
    <b-row>
      <b-col>
        <h2 class="mb-1 page-section-header">{{ degreeName }}</h2>
        <div class="faint-text font-size-16 font-weight-500 pb-2">
          {{ updatedAtDescription }}
        </div>
      </b-col>
      <b-col>
        <div class="d-flex justify-content-end">
          <div class="pr-2">
            <router-link
              id="print-degree-plan"
              :to="`/student/${student.uid}/degree/${templateId}/print`"
            >
              <font-awesome class="mr-1" icon="print" />
              Print Plan
            </router-link>
          </div>
          <div class="pr-2">
            |
          </div>
          <div class="pr-2">
            <router-link
              id="view-degree-history"
              :to="`/student/${student.uid}/degree/history`"
            >
              View Degree History
            </router-link>
          </div>
          <div v-if="$currentUser.canEditDegreeProgress" class="pr-2">
            |
          </div>
          <div v-if="$currentUser.canEditDegreeProgress" class="pr-2">
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
    <b-row class="pt-3">
      <b-col>
        <h3 class="font-size-20 font-weight-bold">Degree Notes</h3>
        <div>
          There are currently no degree notes for this student.
          <b-btn id="create-degree-note-btn" class="pl-0" variant="link">
            Create new degree note
          </b-btn>
        </div>
      </b-col>
      <b-col>
        <div class="align-items-top d-flex justify-content-end">
          <div class="pr-3">
            Show notes when printed
          </div>
          <div :class="{'text-success': includeNotesWhenPrint, 'text-danger': !includeNotesWhenPrint}">
            <div class="d-flex">
              <div class="toggle-label">
                {{ includeNotesWhenPrint ? 'Yes' : 'No' }}
              </div>
              <b-form-checkbox v-model="includeNotesWhenPrint" switch />
            </div>
          </div>
        </div>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import DegreeEditSession from '@/mixins/DegreeEditSession'
import {getCalnetProfileByUid} from '@/api/user'

export default {
  name: 'StudentDegreeCheckHeader',
  mixins: [DegreeEditSession],
  props: {
    student: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    updatedAtDescription: undefined,
    includeNotesWhenPrint: false
  }),
  created() {
    const updatedAtDate = new Date(this.updatedAt)
    const isFresh = new Date(this.createdAt) === updatedAtDate
    const uid = isFresh ? this.createdBy : this.updatedBy
    getCalnetProfileByUid(uid).then(data => {
      const name = data.name || `${data.uid} (UID)`
      this.updatedAtDescription = `${isFresh ? 'Created' : 'Last updated'} by ${name} on ${this.$moment(updatedAtDate).format('MMM D, YYYY')}`
    })
  }
}
</script>

<style scoped>
.toggle-label {
  font-size: 14px;
  font-weight: bolder;
  padding: 2px 8px 0 0;
  width: 30px;
}
</style>
