<template>
  <div :id="`note-${note.id}-outer`" class="advising-note-outer width-90">
    <div
      :id="`note-${note.id}-is-closed`"
      class="w-100"
      :class="{'note-snippet-when-closed': !isOpen}"
    >
      <span v-if="note.isDraft" :id="`note-${note.id}-is-draft`">
        <span class="pr-2">
          <v-chip
            class="font-weight-black"
            color="error"
            density="compact"
            rounded
            size="small"
            variant="flat"
          >
            Draft
          </v-chip>
        </span>
        <span :id="`note-${note.id}-subject`">{{ note.subject || contextStore.config.draftNoteSubjectPlaceholder }}</span>
      </span>
      <span v-if="!note.isDraft">
        <span v-if="note.subject" :id="`note-${note.id}-subject`">{{ note.subject }}</span>
        <span v-if="!note.subject && size(note.message)" :id="`note-${note.id}-subject`">
          <span v-if="isOpen" v-html="note.message" />
          <span v-if="!isOpen" v-html="stripHtmlAndTrim(note.message).replace(/\n\r/g, ' ')" />
        </span>
        <span v-if="!note.subject && !size(note.message) && note.category" :id="`note-${note.id}-subject`">{{ note.category }}<span v-if="note.subcategory">, {{ note.subcategory }}</span></span>
        <span v-if="!note.subject && !size(note.message) && !note.category && !note.eForm" :id="`note-${note.id}-category-closed`">{{ !isEmpty(note.author.departments) ? note.author.departments[0].name : '' }}
          advisor {{ author.name }}<span v-if="note.topics && size(note.topics)">: {{ oxfordJoin(note.topics) }}</span>
        </span>
        <span v-if="!note.subject && !size(note.message) && !note.category && note.eForm" :id="`note-${note.id}-subject`">
          eForm: {{ note.eForm.action }} &mdash; {{ note.eForm.status }}
        </span>
      </span>
    </div>
    <div v-if="isOpen" :id="`note-${note.id}-is-open`" class="pb-2 w-100">
      <div v-if="note.subject && note.message" class="open-note-message-container pt-2">
        <span :id="`note-${note.id}-message-open`" v-html="note.message" />
      </div>
      <div v-if="!note.subject && !note.message && note.eForm" class="pt-2">
        <dl :id="`note-${note.id}-message-open`">
          <div>
            <dt>Term</dt>
            <dd>{{ termNameForSisId(note.eForm.term) }}</dd>
          </div>
          <div>
            <dt>Course</dt>
            <dd>{{ note.eForm.sectionId }} {{ note.eForm.courseName }} - {{ note.eForm.courseTitle }} {{ note.eForm.section }}</dd>
          </div>
          <div>
            <dt>Action</dt>
            <dd>
              {{ note.eForm.action }}
              <span v-if="note.eForm.action === 'Late Grading Basis Change' && note.eForm.gradingBasis"> from <span class="font-italic">{{ note.eForm.gradingBasis }}</span></span>
              <span v-if="note.eForm.action === 'Late Grading Basis Change' && note.eForm.requestedGradingBasis"> to <span class="font-italic">{{ note.eForm.requestedGradingBasis }}</span></span>
              <span v-if="note.eForm.action === 'Unit Change' && note.eForm.unitsTaken"> from <span class="font-italic">{{ numFormat(note.eForm.unitsTaken, '0.0') }}</span>{{ 1 === toInt(note.eForm.unitsTaken) ? ' unit' : ' units' }}</span>
              <span v-if="note.eForm.action === 'Unit Change' && note.eForm.requestedUnitsTaken"> to <span class="font-italic">{{ numFormat(note.eForm.requestedUnitsTaken, '0.0') }}</span>{{ 1 === toInt(note.eForm.requestedUnitsTaken) ? ' unit' : ' units' }}</span>
            </dd>
          </div>
          <div>
            <dt>Form ID</dt>
            <dd>{{ note.eForm.id }}</dd>
          </div>
          <div>
            <dt>Date Initiated</dt>
            <dd>{{ DateTime.fromJSDate(note.createdAt).toFormat('MM/dd/yyyy') }}</dd>
          </div>
          <div>
            <dt>Form Status </dt>
            <dd>{{ note.eForm.status }}</dd>
          </div>
          <div>
            <dt>Final Date &amp; Time Stamp</dt>
            <dd>{{ DateTime.fromJSDate(note.updatedAt).toFormat('MM/dd/yyyy h:mm:ssa') }}</dd>
          </div>
        </dl>
      </div>
      <div v-if="!isNil(author) && !author.name && !author.email && !note.eForm" class="font-size-14 pt-2 text-medium-emphasis">
        Advisor profile not found
        <span v-if="note.legacySource" class="font-italic">
          (note imported from {{ note.legacySource }})
        </span>
      </div>
      <div v-if="author" class="pt-2">
        <div v-if="author.name || author.email">
          <span class="sr-only">Note created by </span>
          <a
            v-if="author.uid && author.name"
            :id="`note-${note.id}-author-name`"
            :aria-label="`${author.name} (link opens UC Berkeley Directory page in a new window)`"
            :href="`https://www.berkeley.edu/directory/results?search-term=${author.name}`"
            target="_blank"
          >
            {{ author.name }}
          </a>
          <span v-if="!author.uid && author.name" :id="`note-${note.id}-author-name`">
            {{ author.name }}
          </span>
          <span v-if="!author.uid && !author.name && author.email" :id="`note-${note.id}-author-email`">
            {{ author.email }}
          </span>
          <span v-if="author.role || author.title">
            - <span :id="`note-${note.id}-author-role`">{{ author.role || author.title }}</span>
          </span>
          <span v-if="note.legacySource" class="font-italic text-medium-emphasis">
            (note imported from {{ note.legacySource }})
          </span>
        </div>
        <div v-if="size(author.departments)" class="text-medium-emphasis">
          <div v-for="(deptName, index) in authorDepartments" :key="index">
            <span :id="`note-${note.id}-author-dept-${index}`">{{ deptName }}</span>
          </div>
        </div>
      </div>
      <div v-if="note.topics && size(note.topics)" class="py-2">
        <AdvisingNoteTopics :note="note" read-only />
      </div>
      <div v-if="note.contactType" class="py-2">
        <div class="font-weight-bold">Contact Type</div>
        <div :id="`note-${note.id}-contact-type`">{{ note.contactType }}</div>
      </div>
      <div v-if="!note.legacySource || size(note.attachments)" class="note-attachments-container">
        <AdvisingNoteAttachments
          :add-attachments="addNoteAttachments"
          :aria-labelledby="`note-${note.id}-attachments-list-label`"
          class="attachments-edit py-3"
          :disabled="!!(isUpdatingAttachments || noteStore.boaSessionExpired)"
          downloadable
          :id-prefix="`note-${note.id}-`"
          :note="note"
          :read-only="!!note.legacySource"
          :remove-attachment="removeAttachmentByIndex"
        >
          <template #label>
            <label
              :id="`note-${note.id}-attachments-list-label`"
              class="font-size-16 font-weight-bold"
              :for="`note-${note.id}-attachments-list`"
            >
              Attachments
            </label>
          </template>
        </AdvisingNoteAttachments>
      </div>
    </div>
    <AreYouSureModal
      v-model="showConfirmDeleteAttachment"
      button-label-confirm="Delete"
      :function-cancel="cancelRemoveAttachment"
      :function-confirm="confirmedRemoveAttachment"
      modal-header="Delete Attachment"
    >
      Are you sure you want to delete the <strong>'{{ displayName(note.attachments, deleteAttachmentIndex) }}'</strong> attachment?
    </AreYouSureModal>
  </div>
</template>

<script setup>
import AdvisingNoteAttachments from '@/components/note/AdvisingNoteAttachments'
import AdvisingNoteTopics from '@/components/note/AdvisingNoteTopics'
import AreYouSureModal from '@/components/util/AreYouSureModal'
import {addAttachments, removeAttachment} from '@/api/notes'
import {alertScreenReader, numFormat, oxfordJoin, toInt} from '@/lib/utils'
import {computed, onMounted, ref, watch} from 'vue'
import {get, isEmpty, isNil, isNumber, map, orderBy, size} from 'lodash'
import {DateTime} from 'luxon'
import {getBoaUserRoles, termNameForSisId} from '@/berkeley'
import {getCalnetProfileByCsid, getCalnetProfileByUid} from '@/api/user'
import {stripHtmlAndTrim} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

const props = defineProps({
  afterSaved: {
    required: true,
    type: Function
  },
  deleteNote: {
    required: true,
    type: Function
  },
  editNote: {
    required: true,
    type: Function
  },
  isOpen: {
    required: true,
    type: Boolean
  },
  note: {
    required: true,
    type: Object
  }
})

const contextStore = useContextStore()
const noteStore = useNoteStore()

const addAttachmentInputElementId = `note-${props.note.id}-choose-file-for-note-attachment`
const author = ref(get(props.note, 'author'))
const authorDepartments = computed(() => orderBy(map(author.value.departments, 'name')))
const deleteAttachmentIndex = ref(undefined)
const isUpdatingAttachments = ref(false)
const showConfirmDeleteAttachment = ref(false)

watch(() => props.isOpen, () => {
  loadAuthorDetails()
})

onMounted(() => {
  loadAuthorDetails()
})

const addNoteAttachments = attachments => {
  return new Promise(resolve => {
    isUpdatingAttachments.value = true
    noteStore.setModel(props.note)
    addAttachments(props.note.id, attachments).then(updatedNote => {
      props.afterSaved(updatedNote, addAttachmentInputElementId)
      noteStore.setAttachments(updatedNote.attachments)
      alertScreenReader('Attachment added', 'assertive')
      isUpdatingAttachments.value = false
      resolve()
    })
  })
}

const cancelRemoveAttachment = () => {
  showConfirmDeleteAttachment.value = false
  deleteAttachmentIndex.value = null
}

const confirmedRemoveAttachment = () => {
  showConfirmDeleteAttachment.value = false
  const attachment = props.note.attachments[deleteAttachmentIndex.value]
  if (attachment && attachment.id) {
    return removeAttachment(props.note.id, attachment.id).then(updatedNote => {
      alertScreenReader(`Attachment '${attachment.displayName}' removed`)
      props.afterSaved(updatedNote, addAttachmentInputElementId)
    })
  }
}

const displayName = (attachments, index) => {
  return !isNumber(index) || size(attachments) <= index ? '' : attachments[index].displayName
}

const loadAuthorDetails = () => {
  const requiresLazyLoad = (
    props.isOpen &&
    (
      !get(props.note, 'author.name') ||
      !get(props.note, 'author.role') ||
      get(author.value, 'uid') !== get(props.note, 'author.uid') ||
      get(author.value, 'sid') !== get(props.note, 'author.sid')
    )
  )
  if (requiresLazyLoad) {
    const hasIdentifier = get(props.note, 'author.uid') || get(props.note, 'author.sid')
    if (hasIdentifier) {
      const author_uid = props.note.author.uid
      const callback = data => {
        author.value = data
        author.value.role = author.value.role || author.value.title
        if (!author.value.role && author.value.departments.length) {
          author.value.role = oxfordJoin(getBoaUserRoles(author.value, author.value.departments[0]))
        }
      }
      if (author_uid) {
        if (author_uid === contextStore.currentUser.uid) {
          callback(contextStore.currentUser)
        } else {
          getCalnetProfileByUid(author_uid).then(callback)
        }
      } else if (props.note.author.sid) {
        getCalnetProfileByCsid(props.note.author.sid).then(callback)
      }
    }
  }
}

const removeAttachmentByIndex = index => {
  deleteAttachmentIndex.value = index
  showConfirmDeleteAttachment.value = true
}
</script>

<style>
.open-note-message-container ul {
  margin: 0 30px 0 30px;
}
</style>

<style scoped>
.advising-note-outer {
  box-sizing: border-box;
}
.attachments-edit {
  box-sizing: border-box;
  max-width: 100%;
  width: 100%;
}
.open-note-message-container {
  overflow-wrap: break-word;
}
.width-90 {
  width: 90%;
}
.note-attachments-container {
  width: 90%;
}
.note-snippet-when-closed {
  height: 24px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
