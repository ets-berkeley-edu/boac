<template>
  <section class="note-comments">
    <div class="font-size-16 font-weight-bold text-medium-emphasis my-2" :class="{'sr-only': !size(note.comments)}">Comments</div>
    <article
      v-for="comment in note.comments"
      :key="comment.id"
      class="border-t-sm d-flex justify-space-between py-2 pl-2"
    >
      <div v-if="!editingComment || editingComment.id !== comment.id" class="flex-grow-1 pr-3">
        <div class="d-flex align-center text-body-1 mb-2">
          <span class="sr-only">comment </span>
          <span class="font-weight-bold pr-1">From:&nbsp;</span>
          <AuthorDetails
            :author="comment.author"
            :id-prefix="`note-${note.id}-comment-${comment.id}`"
          />
        </div>
        <div :id="`note-${note.id}-comment-${comment.id}-text`" v-html="comment.body" />
        <AdvisingNoteAttachments
          v-if="size(comment.attachments)"
          :attachments="comment.attachments"
          class="attachments-edit pt-3"
          :disabled="false"
          :id-prefix="`note-${note.id}-comment-${comment.id}`"
          :is-downloadable="true"
          is-read-only
          label-class="text-medium-emphasis"
          :note="note"
        />
      </div>
      <EditNoteComment
        v-if="!readOnly && editingComment && editingComment.id === comment.id"
        :cancel="onCancelEdit"
        class="pb-3"
        :comment="editingComment"
        :id-prefix="`note-${note.id}-comment-${editingComment.id}`"
        :save="updateComment"
      />
      <footer v-if="!editingComment || editingComment.id !== comment.id" class="academic-timeline-column-date">
        <v-btn
          v-if="!readOnly && canUserEditNote(comment, currentUser)"
          :id="`note-${note.id}-comment-${comment.id}-edit-btn`"
          class="mb-2"
          color="primary"
          density="compact"
          :disabled="isCreatingComment"
          slim
          text="Edit Comment"
          variant="text"
          @click="onClickEdit(comment)"
        />
        <div class="pl-2">
          <div class="font-size-14 text-medium-emphasis">Replied:</div>
          <TimelineDate
            :id="`note-${note.id}-comment-${comment.id}-created-at`"
            :date="comment.createdAt"
            :include-time-of-day="comment.createdAt.length > 10"
            class="mb-2"
          />
        </div>
        <div v-if="comment.updatedAt && comment.createdAt !== comment.updatedAt" class="pl-2">
          <div class="font-size-14 text-medium-emphasis">Edited:</div>
          <TimelineDate
            :id="`note-${note.id}-comment-${comment.id}-updated-at`"
            :date="comment.updatedAt"
            :include-time-of-day="comment.updatedAt.length > 10"
            class="mb-2"
          />
        </div>
      </footer>
    </article>
    <div v-if="!readOnly" class="border-t-sm pt-2">
      <v-btn
        v-if="!isCreatingComment && !editingComment"
        :id="`note-${note.id}-add-comment-btn`"
        class="bg-white my-2"
        color="primary"
        :prepend-icon="mdiPlus"
        text="Add Comment"
        variant="outlined"
        @click="onClickAdd"
      />
    </div>
    <EditNoteComment
      v-if="isCreatingComment"
      :cancel="onCancelAdd"
      :id-prefix="`note-${note.id}-comment-new`"
      :parent-note-id="note.id"
      :save="createComment"
    />
  </section>
</template>

<script setup lang="ts">
import {mdiPlus} from '@mdi/js'
import {ref} from 'vue'
import {size} from 'lodash'
import AdvisingNoteAttachments from '@/components/note/AdvisingNoteAttachments'
import AuthorDetails from '@/components/note/AuthorDetails'
import EditNoteComment from '@/components/note/comment/EditNoteComment'
import TimelineDate from '@/components/student/profile/TimelineDate'
import {addNoteComment, updateNoteComment} from '@/api/notes'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {canUserEditNote} from '@/lib/note.js'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  note: {
    required: true,
    type: Object
  },
  readOnly: {
    required: false,
    type: Boolean
  }
})

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const editingComment = ref()
const isCreatingComment = ref(false)

const onCancelAdd = () => {
  isCreatingComment.value = false
  alertScreenReader('canceled')
  putFocusNextTick(`note-${props.note.id}-add-comment-btn`)
}

const onCancelEdit = () => {
  const commentId = editingComment.value.id
  editingComment.value = undefined
  alertScreenReader('canceled')
  putFocusNextTick(`note-${props.note.id}-comment-${commentId}-edit-btn`)
}

const onClickAdd = () => {
  isCreatingComment.value = true
  putFocusNextTick(`note-${props.note.id}-comment-text`)
}

const onClickEdit = comment => {
  editingComment.value = comment
  putFocusNextTick(`note-${props.note.id}-comment-text`)
}

const createComment = (id, body, attachments) => {
  return addNoteComment(props.note.id, body, attachments).then(() => {
    isCreatingComment.value = false
    alertScreenReader('posted comment')
    putFocusNextTick(`note-${props.note.id}-add-comment-btn`)
  })
}

const updateComment = (id, body, attachments, deleteAttachmentIds) => {
  return updateNoteComment(
    id,
    body,
    attachments,
    deleteAttachmentIds
  ).then(() => {
    editingComment.value = null
    alertScreenReader('updated comment')
    putFocusNextTick(`note-${props.note.id}-comment-${id}-edit-btn`)
  })
}
</script>

<style scoped>
.academic-timeline-column-date{
  margin-right: -24px;
}
</style>
