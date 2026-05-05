<template>
  <section class="note-comments">
    <h4 class="text-medium-emphasis mb-2" :class="{'sr-only': !size(note.comments)}">Comments</h4>
    <article
      v-for="comment in note.comments"
      :key="comment.id"
      class="border-b-sm d-flex justify-space-between py-4 my-2"
    >
      <div v-if="!editingComment || editingComment.id !== comment.id">
        <h5 class="text-body-1 mb-3">
          <span class="sr-only">comment </span>
          <div class="d-flex">
            <span class="font-weight-bold">From:&nbsp;</span>
            <a
              v-if="get(comment, 'author.name')"
              :id="`note-${note.id}-comment-${comment.id}-author-link`"
              :aria-label="`${comment.author.name} UC Berkeley Directory page (opens in new tab)`"
              class="d-flex align-center"
              :href="`https://www.berkeley.edu/directory/results?search-term=${comment.author.name}`"
              target="_blank"
            >
              {{ comment.author.name }} <v-icon class="ml-1" :icon="mdiInformation" size="1rem" />
            </a>
          </div>
        </h5>
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
        v-if="editingComment && editingComment.id === comment.id"
        :cancel="onCancelEdit"
        :comment="editingComment"
        :id-prefix="`note-${note.id}-comment-${editingComment.id}`"
        :save="updateComment"
      />
      <footer v-if="!editingComment || editingComment.id !== comment.id" class="column-date">
        <v-btn
          v-if="canUserEditNote(comment, currentUser)"
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
      </footer>
    </article>
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
    <EditNoteComment
      v-if="isCreatingComment"
      :cancel="onCancelAdd"
      :id-prefix="`note-${note.id}-comment-new`"
      :note="note"
      :save="createComment"
    />
  </section>
</template>

<script setup lang="ts">
import {get, size} from 'lodash'
import {mdiInformation, mdiPlus} from '@mdi/js'
import {ref} from 'vue'
import AdvisingNoteAttachments from '@/components/note/AdvisingNoteAttachments'
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

const createComment = (commentId, body, attachments) => {
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
.column-date {
  width: 12rem;
}
.note-comments {
  margin-right: -14rem;
}
</style>
