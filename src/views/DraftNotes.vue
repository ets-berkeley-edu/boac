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
              variant="link"
              @click="() => openEditModal(row.item)"
            >
              {{ row.item.subject }}
            </b-btn>
            <b-modal
              v-if="showEditModal"
              v-model="showEditModal"
              hide-footer
              hide-header
              size="lg"
              @shown="$putFocusNextTick('modal-header')"
            >
              <EditBatchNoteModal
                :after-cancel="deselectDraftNote"
                :after-saved="afterSave"
                :is-batch-feature="false"
                :note-id="selectedDraftNote.id"
              />
            </b-modal>
          </div>
        </template>
        <template v-slot:cell(author)="row">
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
          <div class="min-width-100 pr-1">
            <b-button
              v-if="!row.item.deletedAt"
              class="float-right mr-2 py-0"
              variant="link"
              @click="openDeleteModal(row.item)"
            >
              <font-awesome
                icon="trash-alt"
                aria-label="Delete"
                class="has-error"
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
        :function-cancel="deselectDraftNote"
        :function-confirm="deleteDraftNote"
        :modal-body="deleteModalBodyText"
        :show-modal="showDeleteModal"
        button-label-confirm="Delete"
        modal-header="Are you sure?"
      />
    </div>
  </div>
</template>

<script>
import AreYouSureModal from '@/components/util/AreYouSureModal.vue'
import Loading from '@/mixins/Loading.vue'
import Scrollable from '@/mixins/Scrollable.vue'
import Spinner from '@/components/util/Spinner.vue'
import TimelineDate from '@/components/student/profile/TimelineDate.vue'
import Util from '@/mixins/Util.vue'
import {deleteNote, getMyDraftNotes} from '@/api/notes'

export default {
  name: 'DraftNotes',
  mixins: [Loading, Scrollable, Util],
  components: {AreYouSureModal, Spinner, TimelineDate},
  data: () => ({
    fields: undefined,
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
        key: 'sids',
        label: 'SID(s)'
      },
      {
        key: 'subject'
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
        label: 'Saved'
      },
      {
        class: 'float-right',
        key: 'delete',
        label: 'Delete'
      }
    )
    this.reloadDraftNotes('Draft notes list is ready.')
    this.$eventHub.on('draft-note-created', () => {
      this.reloadDraftNotes()
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
    afterSave(data) {
      const existing = this.$_.find(this.myDraftNotes, ['id', this.selectedDraftNote.id])
      Object.assign(existing, data)
      this.deselectDraftNote()
    },
    deleteDraftNote() {
      deleteNote(this.selectedDraftNote).then(() => {
        this.deselectDraftNote()
        this.reloadDraftNotes('Draft note deleted')
      })
    },
    deselectDraftNote() {
      this.selectedDraftNote = null
      this.mode = null
    },
    reloadDraftNotes(srAlert) {
      this.scrollToTop()
      getMyDraftNotes().then(data => {
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
