<template>
  <div class="p-3">
    <Spinner />
    <h1 class="page-section-header pl-2 pt-2">
      {{ currentUser.isAdmin ? 'Draft Notes' : 'My Draft Notes' }}
    </h1>
    <div v-if="!loading" class="pr-3">
      <div v-if="!currentUser.isAdmin && myDraftNotes.length" class="font-weight-700 pb-3 pl-2 text-secondary">
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
        <template #cell(student)="row">
          <span v-if="row.item.student">
            <router-link
              :id="`link-to-student-${row.item.student.uid}`"
              :to="studentRoutePath(row.item.student.uid, currentUser.inDemoMode)"
            >
              <span :class="{'demo-mode-blur': currentUser.inDemoMode}">
                {{ row.item.student.firstName }} {{ row.item.student.lastName }}
              </span>
            </router-link>
          </span>
          <span v-if="!row.item.student" class="font-italic">
            &mdash;
          </span>
        </template>
        <template #cell(sid)="row">
          <span :class="{'demo-mode-blur': currentUser.inDemoMode}">
            {{ row.item.sid || '&mdash;' }}
          </span>
        </template>
        <template #cell(subject)="row">
          <div class="align-items-center d-flex justify-content-between">
            <div>
              <div v-if="row.item.author.uid !== currentUser.uid" :class="{'demo-mode-blur': currentUser.inDemoMode}">
                {{ _trim(row.item.subject) || config.draftNoteSubjectPlaceholder }}
              </div>
              <b-btn
                v-if="row.item.author.uid === currentUser.uid"
                :id="`open-draft-note-${row.item.id}`"
                class="border-0 p-0 text-left"
                :class="{'demo-mode-blur': currentUser.inDemoMode}"
                variant="link"
                @click="() => openEditModal(row.item)"
              >
                {{ _trim(row.item.subject) || config.draftNoteSubjectPlaceholder }}
              </b-btn>
            </div>
            <div v-if="_size(row.item.attachments)">
              <span class="sr-only">Has attachment(s)</span>
              <font-awesome icon="paperclip" />
            </div>
          </div>
        </template>
        <template
          v-if="currentUser.isAdmin"
          #cell(author)="row"
        >
          {{ row.item.author.name }}
        </template>
        <template #cell(updatedAt)="row">
          <TimelineDate
            :date="row.item.updatedAt || row.item.createdAt"
            sr-prefix="Draft note saved on"
          />
        </template>
        <template #cell(delete)="row">
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
        {{ currentUser.isAdmin ? 'No' : 'You have no' }} saved drafts.
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
import AreYouSureModal from '@/components/util/AreYouSureModal'
import Context from '@/mixins/Context'
import EditBatchNoteModal from '@/components/note/EditBatchNoteModal'
import Spinner from '@/components/util/Spinner'
import TimelineDate from '@/components/student/profile/TimelineDate'
import Util from '@/mixins/Util'
import {deleteNote, getMyDraftNotes} from '@/api/notes'

export default {
  name: 'DraftNotes',
  components: {AreYouSureModal, EditBatchNoteModal, Spinner, TimelineDate},
  mixins: [Context, Util],
  data: () => ({
    activeOperation: undefined,
    fields: undefined,
    isDeleting: false,
    myDraftNotes: undefined,
    selectedDraftNote: undefined
  }),
  computed: {
    deleteModalBodyText() {
      let message
      if (this.selectedDraftNote) {
        const student = this.selectedDraftNote.student
        const style = this.currentUser.inDemoMode ? 'demo-mode-blur' : ''
        message = 'Please confirm the deletion of the draft note '
        message += student ? `for <b class="${style}">${student.firstName} ${student.lastName}</b>.` : `with subject ${this.selectedDraftNote.subject}.`
      }
      return message
    },
    showEditModal: {
      get() {
        return !!this.selectedDraftNote && this.activeOperation === 'edit'
      },
      set(value) {
        if (!value) {
          this.deselectDraftNote()
        }
      }
    },
    showDeleteModal: {
      get() {
        return !!this.selectedDraftNote && this.activeOperation === 'delete'
      },
      set(value) {
        if (!value) {
          this.deselectDraftNote()
        }
      }
    }
  },
  created() {
    this.fields = [
      {
        class: 'w-25',
        key: 'student',
        label: 'Student'
      },
      {
        class: 'w-5',
        key: 'sid',
        label: 'SID'
      },
      {
        class: 'w-auto',
        key: 'subject',
        label: 'Subject'
      }
    ]
    if (this.currentUser.isAdmin) {
      this.fields.push(
        {
          class: 'w-15',
          key: 'author',
          label: 'Author'
        }
      )
    }
    this.fields.push(
      {
        class: 'text-nowrap w-5',
        key: 'updatedAt',
        label: 'Date'
      },
      {
        class: 'w-5',
        key: 'delete',
        label: 'Delete'
      }
    )
    this.reloadDraftNotes('Draft notes list is ready.')
    this.setEventHandler('note-created', () => {
      this.reloadDraftNotes()
    })
    this.setEventHandler('note-deleted', noteId => {
      if (this._find(this.myDraftNotes, ['id', noteId])) {
        this.reloadDraftNotes()
      }
    })
    this.setEventHandler('note-updated', note => {
      if (this._find(this.myDraftNotes, ['id', note.id])) {
        this.reloadDraftNotes()
      }
    })
  },
  methods: {
    afterEditDraft(data) {
      const existing = this._find(this.myDraftNotes, ['id', data.id])
      if (existing) {
        Object.assign(existing, data)
        this.reloadDraftNotes().then(() => {
          this.deselectDraftNote()
        })
      } else {
        this.deselectDraftNote()
      }
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
      this.activeOperation = null
    },
    reloadDraftNotes(srAlert) {
      return getMyDraftNotes().then(data => {
        this.myDraftNotes = data
        if (srAlert) {
          this.loadingComplete(srAlert)
        }
      })
    },
    openDeleteModal(draftNote) {
      this.activeOperation = 'delete'
      this.selectedDraftNote = draftNote
      this.alertScreenReader('Please confirm draft note deletion.')
    },
    openEditModal(noteDraft) {
      this.activeOperation = 'edit'
      this.selectedDraftNote = noteDraft
    }
  }
}
</script>
