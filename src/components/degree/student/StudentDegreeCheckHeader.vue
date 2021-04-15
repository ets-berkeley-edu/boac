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
  }
}
</script>
