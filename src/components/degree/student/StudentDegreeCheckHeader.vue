<template>
  <b-container class="px-0 mx-0" :fluid="true">
    <b-row>
      <b-col>
        <h2 class="mb-1 page-section-header">{{ degreeName }}</h2>
        <div class="faint-text font-weight-500 font-size-18">
          Last updated {{ updatedAt | moment('MMM D, YYYY') }}
        </div>
      </b-col>
      <b-col>
        <div class="d-flex justify-content-end">
          <div class="pr-2">
            <router-link
              id="print-degree-plan"
              :to="`/student/${student.uid}/degree/${degreeId}/print`"
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
          <div class="pr-2">
            |
          </div>
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
export default {
  name: 'StudentDegreeCheckHeader',
  props: {
    degreeId: {
      required: true,
      type: Number
    },
    degreeName: {
      required: true,
      type: String
    },
    student: {
      required: true,
      type: Object
    },
    updatedAt: {
      required: true,
      type: String
    }
  },
  data: () => ({
    includeNotesWhenPrint: false
  })
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
