<template>
  <div class="p-3">
    <Spinner />
    <h1 class="page-section-header">
      Draft Notes
    </h1>
    <div v-if="!loading">
      <b-table
        borderless
        :fields="[
          {
            class: '',
            key: 'students',
            label: 'Student(s)'
          },
          {
            class: '',
            key: 'sids',
            label: 'SID(s)'
          },
          {
            class: '',
            key: 'subject'
          },
          {
            class: '',
            key: 'updatedAt',
            label: 'Saved'
          }
        ]"
        hover
        :items="myNoteDrafts"
        responsive
        stacked="md"
        thead-class="text-nowrap text-secondary text-uppercase"
      >
        <template v-slot:cell(students)="row">
          <span v-if="row.item.students.length === 1">
            <router-link
              :id="`link-to-student-${row.item.students[0].uid}`"
              :to="studentRoutePath(row.item.students[0].uid, $currentUser.inDemoMode)"
            >
              <span :class="{'demo-mode-blur': $currentUser.inDemoMode}">
                {{ row.item.students[0].firstName }} {{ row.item.students[0].lastName }}
              </span>
            </router-link>
          </span>
          <span v-if="row.item.students.length > 1" class="font-italic">
            Multiple ({{ row.item.students.length }})
          </span>
        </template>
        <template v-slot:cell(sids)="row">
          <span v-if="row.item.sids.length === 1">
            {{ row.item.sids[0] }}
          </span>
          <span v-if="row.item.sids.length > 1" class="font-italic">
            Multiple
          </span>
        </template>
        <template v-slot:cell(subject)="row">
          {{ row.item.subject }}
        </template>
        <template v-slot:cell(updatedAt)="row">
          <TimelineDate :date="row.item.updatedAt" sr-prefix="Draft note saved on" />
        </template>
      </b-table>
    </div>
  </div>
</template>

<script>
import Loading from '@/mixins/Loading.vue'
import Scrollable from '@/mixins/Scrollable.vue'
import Spinner from '@/components/util/Spinner.vue'
import TimelineDate from '@/components/student/profile/TimelineDate.vue'
import Util from '@/mixins/Util.vue'
import {getMyNoteDrafts} from '@/api/note-drafts'

export default {
  name: 'DraftNotes',
  mixins: [Loading, Scrollable, Util],
  components: {Spinner, TimelineDate},
  data: () => ({
    myNoteDrafts: undefined
  }),
  created() {
    this.scrollToTop()
    getMyNoteDrafts().then(data => {
      this.myNoteDrafts = data
      this.loaded('Draft notes list is ready.')
    })
  }
}
</script>
