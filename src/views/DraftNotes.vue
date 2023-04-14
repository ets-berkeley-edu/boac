<template>
  <div class="p-3">
    <Spinner />
    <h1 class="page-section-header">
      Draft Notes
    </h1>
    <div v-if="!loading">
      <b-table
        v-if="myDraftNotes.length"
        borderless
        :fields="fields"
        hover
        :items="myDraftNotes"
        responsive
        stacked="md"
        thead-class="text-nowrap text-secondary text-uppercase"
      >
        <template v-slot:cell(student)="row">
          <span v-if="row.item.student">
            <router-link
              :id="`link-to-student-${row.item.student.uid}`"
              :to="studentRoutePath(row.item.student.uid, $currentUser.inDemoMode)"
            >
              <span :class="{'demo-mode-blur': $currentUser.inDemoMode}">
                {{ row.item.student.firstName }} {{ row.item.student.lastName }}
              </span>
            </router-link>
          </span>
          <span v-if="!row.item.student" class="font-italic">
            &mdash;
          </span>
        </template>
        <template v-slot:cell(sids)="row">
          {{ row.item.sid || '&mdash;' }}
        </template>
        <template v-slot:cell(subject)="row">
          <div class="truncate-with-ellipsis">
            <span v-if="row.item.author.uid !== $currentUser.uid">
              {{ row.item.subject }}
            </span>
            <b-btn
              v-if="row.item.author.uid === $currentUser.uid"
              :id="`open-draft-note-${row.item.id}`"
              class="border-0 p-0"
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
              <EditAdvisingNote
                :after-cancel="afterCancelEdit"
                :after-saved="afterSaveDraftNote"
                :note-id="editingDraftNoteId"
              />
            </b-modal>
          </div>
        </template>
        <template v-slot:cell(updatedAt)="row">
          <TimelineDate
            :date="row.item.updatedAt || row.item.createdAt"
            sr-prefix="Draft note saved on"
          />
        </template>
        <template v-slot:cell(delete)="row">
          <div class="float-right min-width-100">
            <b-button
              v-if="!row.item.deletedAt"
              class="px-0 py-0"
              variant="link"
              @click="openDeleteModal(row.item)"
            >
              <font-awesome
                icon="trash-alt"
                aria-label="Delete"
                class="text-secondary"
                title="Delete"
              />
            </b-button>
          </div>
        </template>
      </b-table>
      <div v-if="!myDraftNotes.length">
        You have no saved drafts.
      </div>
    </div>
  </div>
</template>

<script>
import EditAdvisingNote from '@/components/note/EditAdvisingNote.vue'
import Loading from '@/mixins/Loading.vue'
import Scrollable from '@/mixins/Scrollable.vue'
import Spinner from '@/components/util/Spinner.vue'
import TimelineDate from '@/components/student/profile/TimelineDate.vue'
import Util from '@/mixins/Util.vue'
import {getMyDraftNotes} from '@/api/notes'

export default {
  name: 'DraftNotes',
  mixins: [Loading, Scrollable, Util],
  components: {EditAdvisingNote, Spinner, TimelineDate},
  data: () => ({
    draftNoteToDelete: undefined,
    editingDraftNoteId: undefined,
    fields: [
      {
        class: '',
        key: 'student',
        label: 'Student'
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
      },
      {
        class: '',
        key: 'delete',
        label: 'Delete'
      }
    ],
    myDraftNotes: undefined
  }),
  created() {
    this.scrollToTop()
    getMyDraftNotes().then(data => {
      this.myDraftNotes = data
      this.loaded('Draft notes list is ready.')
    })
  },
  computed: {
    showEditUserModal: {
      get() {
        return !!this.editingDraftNoteId
      },
      set(value) {
        if (!value) {
          this.editingDraftNoteId = null
        }
      }
    }
  },
  methods: {
    afterCancelEdit() {
      this.editingDraftNoteId = null
    },
    afterSaveDraftNote(data) {
      const existing = this.$_.find(this.myDraftNotes, ['id', this.editingDraftNoteId])
      Object.assign(existing, data)
      this.editingDraftNoteId = null
    },
    openDeleteModal(draftNote) {
      this.draftNoteToDelete = draftNote
      this.$announcer.polite('Please confirm draft note deletion.')
    },
    openDraftNote(noteDraftId) {
      this.editingDraftNoteId = noteDraftId
    }
  }
}
</script>
