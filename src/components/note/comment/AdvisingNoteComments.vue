<template>
  <section class="note-comments">
    <h4 class="text-medium-emphasis mb-2">Comments</h4>
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
            <a class="d-flex align-center" href="">
              John Lee <v-icon class="ml-1" :icon="mdiInformation" size="1rem" />
            </a>
          </div>
        </h5>
        <p>lorem ipsum</p>
      </div>
      <EditNoteComment
        v-if="editingComment && editingComment.id === comment.id"
        :cancel="onCancelEdit"
        :comment="editingComment"
        :id-prefix="`note-${note.id}-comment-${editingComment.id}`"
        :note="note"
        :save="updateComment"
      />
      <footer v-if="!editingComment || editingComment.id !== comment.id" class="column-date">
        <v-btn
          :id="`note-${note.id}-comment-${comment.id}-edit-btn`"
          class="mb-2"
          color="primary"
          density="compact"
          :disabled="isCreatingComment"
          text="Edit Comment"
          variant="text"
          @click="onClickEdit(comment)"
        />
        <div class="text-medium-emphasis">Replied:</div>
        <div>Dec 18, 2023 @ 3:08PM</div>
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
import {mdiInformation, mdiPlus} from '@mdi/js'
import {ref} from 'vue'
import EditNoteComment from '@/components/note/comment/EditNoteComment'
import {addNoteComment, updateNote} from '@/api/notes'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'

const props = defineProps({
  note: {
    required: true,
    type: Object
  }
})

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

const createComment = (body, attachments) => {
  return addNoteComment(props.note.id, body, attachments).then(() => {
    isCreatingComment.value = false
    alertScreenReader('posted comment')
    putFocusNextTick(`note-${props.note.id}-add-comment-btn`)
  })
}

const updateComment = (body, attachments, commentId) => {
  return updateNote(
    commentId,
    body,
    attachments,
    props.note.id
  ).then(() => {
    editingComment.value = null
    alertScreenReader('updated comment')
    putFocusNextTick(`note-${props.note.id}-comment-${commentId}-edit-btn`)
  })
}
</script>

<style scoped>
.note-comments {
  margin-right: -12rem;
}
</style>
