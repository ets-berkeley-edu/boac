<template>
  <div class="p-3">
    <Spinner />
    <h1 class="page-section-header pl-2 pt-3">
      {{ $currentUser.isAdmin ? 'Draft Notes' : 'My Draft Notes' }}
    </h1>
    <div v-if="!loading" class="pr-3">
      <div v-if="!$currentUser.isAdmin && myDraftNotes.length" class="font-weight-700 pb-3 pl-2 text-secondary">
        A draft note is only visible to its author.
      </div>
      <b-table
        v-if="myDraftNotes.length"
        borderless
        :fields="fields"
        hover
        :items="myDraftNotes"
        responsive
        stacked="md"
        thead-class="text-nowrap text-secondary text-uppercase"
        :tbody-tr-attr="item => ({id: `draft-note-${item.id}`})"
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
        <template v-slot:cell(sid)="row">
          <span :class="{'demo-mode-blur': $currentUser.inDemoMode}">
            {{ row.item.sid || '&mdash;' }}
          </span>
        </template>
        <template v-slot:cell(subject)="row">
          <div>
            <div v-if="row.item.author.uid !== $currentUser.uid" :class="{'demo-mode-blur': $currentUser.inDemoMode}">
              {{ row.item.subject }}
            </div>
            <b-btn
              v-if="row.item.author.uid === $currentUser.uid"
              :id="`open-draft-note-${row.item.id}`"
              class="border-0 p-0"
              :class="{'demo-mode-blur': $currentUser.inDemoMode}"
              variant="link"
              @click="() => openEditModal(row.item)"
            >
              {{ row.item.subject }}
            </b-btn>
          </div>
        </template>
        <template
          v-if="$currentUser.isAdmin"
          v-slot:cell(author)="row"
        >
          {{ row.item.author.name }}
        </template>
        <template v-slot:cell(updatedAt)="row">
          <TimelineDate
            :date="row.item.updatedAt"
            sr-prefix="Draft note saved on"
          />
        </template>
        <template v-slot:cell(setDate)="row">
          <TimelineDate
            :date="row.item.setDate || row.item.updatedAt || row.item.createdAt"
            sr-prefix="Draft note saved on"
          />
        </template>
        <template v-slot:cell(delete)="row">
          <div class="min-width-100 pl-2 pr-1">
            <b-button
              v-if="!row.item.deletedAt"
              class="mr-2 py-0"
              :disabled="isDeleting"
              variant="link"
              @click="openDeleteModal(row.item)"
            >
              <font-awesome
                icon="trash-alt"
                aria-label="Delete"
                :class="isDeleting ? 'text-secondary' : 'has-error'"
                title="Delete"
              />
            </b-button>
          </div>
        </template>
      </b-table>
      <div v-if="!myDraftNotes.length" class="pl-2 pt-2">
        {{ $currentUser.isAdmin ? 'No' : 'You have no' }} saved drafts.
      </div>
      <AreYouSureModal
        v-if="showDeleteModal"
        :button-label-confirm="isDeleting ? 'Deleting' : 'Delete'"
        :function-cancel="deselectDraftNote"
        :function-confirm="deleteDraftNote"
        :modal-body="deleteModalBodyText"
        modal-header="Are you sure?"
        :show-modal="showDeleteModal"
      />
    </div>
    <EditBatchNoteModal
      v-if="showEditModal"
      v-model="showEditModal"
      initial-mode="editDraft"
      :note-id="selectedDraftNote.id"
      :on-close="afterEditDraft"
      :sid="selectedDraftNote.sid"
    />
  </div>
</template>

<script>
import AreYouSureModal from '@/components/util/AreYouSureModal.vue'
import EditBatchNoteModal from '@/components/note/EditBatchNoteModal.vue'
import Loading from '@/mixins/Loading.vue'
import Scrollable from '@/mixins/Scrollable.vue'
import Spinner from '@/components/util/Spinner.vue'
import TimelineDate from '@/components/student/profile/TimelineDate.vue'
import Util from '@/mixins/Util.vue'
import {deleteNote, getMyDraftNotes} from '@/api/notes'

export default {
  name: 'DraftNotes',
  mixins: [Loading, Scrollable, Util],
  components: {AreYouSureModal, EditBatchNoteModal, Spinner, TimelineDate},
  data: () => ({
    fields: undefined,
    isDeleting: false,
    mode: undefined,
    myDraftNotes: undefined,
    selectedDraftNote: undefined
  }),
  created() {
    this.fields = [
      {
        key: 'student',
        label: 'Student'
      },
      {
        key: 'sid',
        label: 'SID'
      },
      {
        key: 'subject',
        label: 'Subject'
      }
    ]
    if (this.$currentUser.isAdmin) {
      this.fields.push(
        {
          key: 'author',
          label: 'Author'
        }
      )
    }
    this.fields.push(
      {
        key: 'setDate',
        label: 'Date'
      },
      {
        key: 'delete',
        label: 'Delete'
      }
    )
    this.reloadDraftNotes('Draft notes list is ready.')
    this.$eventHub.on('note-created', () => {
      this.reloadDraftNotes()
    })
    this.$eventHub.on('note-deleted', noteId => {
      if (this.$_.find(this.myDraftNotes, ['id', noteId])) {
        this.reloadDraftNotes()
      }
    })
    this.$eventHub.on('note-updated', note => {
      if (this.$_.find(this.myDraftNotes, ['id', note.id])) {
        this.reloadDraftNotes()
      }
    })
  },
  computed: {
    deleteModalBodyText() {
      let message
      if (this.selectedDraftNote) {
        const student = this.selectedDraftNote.student
        message = 'Please confirm the deletion of the draft note '
        message += student ? `for <b>${student.firstName} ${student.lastName}</b>.` : `with subject ${this.selectedDraftNote.subject}.`
      }
      return message
    },
    showEditModal: {
      get() {
        return !!this.selectedDraftNote && this.mode === 'edit'
      },
      set(value) {
        if (!value) {
          this.deselectDraftNote()
        }
      }
    },
    showDeleteModal: {
      get() {
        return !!this.selectedDraftNote && this.mode === 'delete'
      },
      set(value) {
        if (!value) {
          this.deselectDraftNote()
        }
      }
    }
  },
  methods: {
    afterEditDraft(data) {
      const existing = this.$_.find(this.myDraftNotes, ['id', this.selectedDraftNote.id])
      Object.assign(existing, data)
      this.reloadDraftNotes().then(() => {
        this.deselectDraftNote()
      })
    },
    deleteDraftNote() {
      return new Promise(resolve => {
        this.isDeleting = true
        deleteNote(this.selectedDraftNote).then(() => {
          this.reloadDraftNotes('Draft note deleted').then(() => {
            this.deselectDraftNote()
            this.isDeleting = false
            resolve()
          })
        })
      })
    },
    deselectDraftNote() {
      this.selectedDraftNote = null
      this.mode = null
    },
    reloadDraftNotes(srAlert) {
      return getMyDraftNotes().then(data => {
        this.myDraftNotes = data
        if (srAlert) {
          this.loaded(srAlert)
        }
      })
    },
    openDeleteModal(draftNote) {
      this.mode = 'delete'
      this.selectedDraftNote = draftNote
      this.$announcer.polite('Please confirm draft note deletion.')
    },
    openEditModal(noteDraft) {
      this.mode = 'edit'
      this.selectedDraftNote = noteDraft
    }
  }
}
</script>
