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
          <div class="ml-1 truncate-with-ellipsis">
            <span v-if="row.item.creatorId !== $currentUser.id">
              {{ row.item.subject }}
            </span>
            <b-btn
              v-if="row.item.creatorId === $currentUser.id"
              :id="`open-draft-note-${row.item.id}`"
              variant="text"
              @click="() => openDraftNote(row.item.id)"
            >
              {{ row.item.subject }}
            </b-btn>
            <b-modal
              v-if="showEditUserModal"
              v-model="showEditUserModal"
              body-class="pl-0 pr-0"
              hide-footer
              hide-header
              @shown="$putFocusNextTick('modal-header')"
            >
              <EditDraftNote
                :after-cancel="afterCancelEdit"
                :after-saved="afterSaveDraftNote"
                :draft-note-id="editingNoteDraftId"
              />
            </b-modal>
          </div>
        </template>
        <template v-slot:cell(updatedAt)="row">
          <TimelineDate :date="row.item.updatedAt" sr-prefix="Draft note saved on" />
        </template>
      </b-table>
    </div>
  </div>
</template>

<script>
import EditDraftNote from '@/components/note/EditDraftNote.vue'
import Loading from '@/mixins/Loading.vue'
import Scrollable from '@/mixins/Scrollable.vue'
import Spinner from '@/components/util/Spinner.vue'
import TimelineDate from '@/components/student/profile/TimelineDate.vue'
import Util from '@/mixins/Util.vue'
import {getMyNoteDrafts} from '@/api/note-drafts'

export default {
  name: 'DraftNotes',
  mixins: [Loading, Scrollable, Util],
  components: {EditDraftNote, Spinner, TimelineDate},
  data: () => ({
    editingNoteDraftId: undefined,
    myNoteDrafts: undefined
  }),
  created() {
    this.scrollToTop()
    getMyNoteDrafts().then(data => {
      this.myNoteDrafts = data
      this.loaded('Draft notes list is ready.')
    })
  },
  computed: {
    showEditUserModal: {
      get() {
        return !!this.editingNoteDraftId
      },
      set(value) {
        if (!value) {
          this.editingNoteDraftId = null
        }
      }
    }
  },
  methods: {
    afterCancelEdit() {
      this.editingNoteDraftId = null
    },
    afterSaveDraftNote(data) {
      const existing = this.$_.find(this.myNoteDrafts, ['id', this.editingNoteDraftId])
      Object.assign(existing, data)
      this.editingNoteDraftId = null
    },
    openDraftNote(noteDraftId) {
      this.editingNoteDraftId = noteDraftId
    }
  }
}
</script>
