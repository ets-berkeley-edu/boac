<template>
  <section class="note-comments">
    <div class="font-size-16 font-weight-bold text-medium-emphasis my-2" :class="{'sr-only': !size(parent.comments)}">Comments</div>
    <article
      v-for="comment in parent.comments"
      :key="comment.id"
      class="border-t-sm d-flex justify-space-between py-2 pl-2"
    >
      <div v-if="!editingComment || editingComment.id !== comment.id" class="flex-grow-1 pr-3">
        <div class="d-flex align-center text-body-1 mb-2">
          <span class="sr-only">comment </span>
          <span class="font-weight-bold pr-1">From:&nbsp;</span>
          <AuthorDetails
            :author="comment.author"
            :id-prefix="`${idPrefix}-comment-${comment.id}`"
            :peer-advising-department-id="comment.peerAdvisingDepartmentId"
          />
        </div>
        <div :id="`${idPrefix}-comment-${comment.id}-text`" v-html="comment.body" />
        <AdvisingNoteAttachments
          v-if="size(comment.attachments)"
          :attachments="comment.attachments"
          class="attachments-edit pt-3"
          :disabled="false"
          :id-prefix="`${idPrefix}-comment-${comment.id}`"
          :is-downloadable="true"
          is-read-only
          label-class="text-medium-emphasis"
          :note="parent"
        />
      </div>
      <EditComment
        v-if="canUserEditNote(comment, currentUser) && editingComment && editingComment.id === comment.id"
        :cancel="onCancelEdit"
        class="pb-2"
        :comment="editingComment"
        :id-prefix="`${idPrefix}-comment-${editingComment.id}`"
        :save="onUpdateComment"
      />
      <footer v-if="!editingComment || editingComment.id !== comment.id" class="academic-timeline-column-date">
        <v-btn
          v-if="canUserEditNote(comment, currentUser)"
          :id="`${idPrefix}-comment-${comment.id}-edit-btn`"
          class="mb-2"
          color="primary"
          density="compact"
          :disabled="isCreatingComment"
          slim
          text="Edit Comment"
          variant="text"
          @click="onClickEdit(comment)"
        />
        <v-btn
          v-if="currentUser.isAdmin"
          :id="`${idPrefix}-comment-${comment.id}-delete-btn`"
          class="mb-2"
          color="primary"
          density="compact"
          :disabled="isCreatingComment"
          slim
          text="Delete Comment"
          variant="text"
          @click="onClickDelete(comment)"
        />
        <div class="pl-2">
          <div class="font-size-14 text-medium-emphasis">Replied:</div>
          <TimelineDate
            :id="`${idPrefix}-comment-${comment.id}-created-at`"
            :date="comment.createdAt"
            :include-time-of-day="comment.createdAt.length > 10"
            class="mb-2"
          />
        </div>
        <div v-if="comment.updatedAt && comment.createdAt !== comment.updatedAt" class="pl-2">
          <div class="font-size-14 text-medium-emphasis">Edited:</div>
          <TimelineDate
            :id="`${idPrefix}-comment-${comment.id}-updated-at`"
            :date="comment.updatedAt"
            :include-time-of-day="comment.updatedAt.length > 10"
            class="mb-2"
          />
        </div>
      </footer>
    </article>
    <div v-if="!editingComment" class="border-t-sm pt-2">
      <v-btn
        v-if="!isCreatingComment"
        :id="`${idPrefix}-add-comment-btn`"
        class="bg-white my-2"
        color="primary"
        :prepend-icon="mdiPlus"
        text="Add Comment"
        variant="outlined"
        @click="onClickAdd"
      />
      <EditComment
        v-if="isCreatingComment"
        :cancel="onCancelAdd"
        class="pb-2"
        :id-prefix="`${idPrefix}-comment-new`"
        :parent-note-id="parent.id"
        :save="createComment"
      />
    </div>
    <AreYouSureModal
      v-model="isDeletingComment"
      button-label-confirm="Delete"
      :function-cancel="onCancelDelete"
      :function-confirm="onConfirmDelete"
      modal-header="Delete note"
    >
      Are you sure you want to delete the comment
      <span v-if="deletingComment">
        containing text "<span class="font-weight-bold text-medium-emphasis">{{ truncate(stripHtmlAndTrim(deletingComment.body), {separator: ' '}) }}</span>"?</span>
    </AreYouSureModal>
  </section>
</template>

<script setup lang="ts">
import {computed, ref} from 'vue'
import {findIndex, includes, size, truncate} from 'lodash'
import {mdiPlus} from '@mdi/js'
import AdvisingNoteAttachments from '@/components/note/AdvisingNoteAttachments'
import AreYouSureModal from '@/components/util/AreYouSureModal.vue'
import AuthorDetails from '@/components/note/AuthorDetails'
import EditComment from '@/components/comment/EditComment'
import TimelineDate from '@/components/student/profile/TimelineDate'
import {addComment, deleteComment, updateComment} from '@/api/comments'
import {addNoteComment, deleteNoteComment, updateNoteComment} from '@/api/notes'
import {addPeerAdvisingNoteComment, updatePeerAdvisingNoteComment} from '@/api/peer-advising-notes'
import {alertScreenReader, putFocusNextTick, stripHtmlAndTrim} from '@/lib/utils'
import {canUserEditNote} from '@/lib/note.js'
import {isPeerAdvisor} from '@/lib/boa-user'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  parent: {
    required: true,
    type: Object
  }
})

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const deletingComment = ref()
const editingComment = ref()
const isCreatingComment = ref(false)

const idPrefix = computed(() => `${props.parent.type}-${props.parent.id}`)
const isDeletingComment = computed(() => !!deletingComment.value)

const onCancelAdd = () => {
  isCreatingComment.value = false
  alertScreenReader('canceled')
  putFocusNextTick(`${idPrefix.value}-add-comment-btn`)
}

const onCancelDelete = () => {
  if (deletingComment.value) {
    alertScreenReader('Canceled')
    putFocusNextTick(`${idPrefix.value}-comment-${deletingComment.value.id}-delete-btn`, {scroll: false})
    deletingComment.value = undefined
  }
}

const onCancelEdit = () => {
  const commentId = editingComment.value.id
  editingComment.value = undefined
  alertScreenReader('canceled')
  putFocusNextTick(`${idPrefix.value}-comment-${commentId}-edit-btn`)
}

const onClickAdd = () => {
  isCreatingComment.value = true
  putFocusNextTick(`${idPrefix.value}-comment-text`)
}

const onClickDelete = comment => {
  deletingComment.value = comment
}

const onClickEdit = comment => {
  editingComment.value = comment
  putFocusNextTick(`${idPrefix.value}-comment-text`)
}

const onConfirmDelete = () => {
  if (deletingComment.value) {
    const doDelete = includes(['appointment', 'eForm'], props.parent.type) ? deleteComment : deleteNoteComment
    const index = findIndex(props.parent.comments, {'id': deletingComment.value.id})
    const lastItemIndex = size(props.parent.comments) - 1
    doDelete(props.parent.id, deletingComment.value.id).then(() => {
      alertScreenReader('Comment deleted')
      deletingComment.value = undefined
      if (lastItemIndex > 0) {
        const nextFocusIndex = (index === lastItemIndex ) ? index - 1 : index
        const nextFocusComment = props.parent.comments[nextFocusIndex]
        putFocusNextTick(`${idPrefix.value}-comment-${nextFocusComment.id}-delete-btn`)
      } else {
        putFocusNextTick(`${idPrefix.value}-add-comment-btn`)
      }
    })
  }
}

const createComment = (id, body, attachments) => {
  let create
  if (isPeerAdvisor(currentUser)) {
    create = addPeerAdvisingNoteComment
  } else if (includes(['appointment', 'eForm'], props.parent.type)) {
    create = addComment
  } else {
    create = addNoteComment
  }
  return create(
    props.parent.id,
    props.parent.parentType || props.parent.type,
    body,
    attachments
  ).then(() => {
    isCreatingComment.value = false
    alertScreenReader('posted comment')
    putFocusNextTick(`${idPrefix.value}-add-comment-btn`)
  })
}

const onUpdateComment = (id, body, attachments, deleteAttachmentIds) => {
  let update
  if (isPeerAdvisor(currentUser)) {
    update = updatePeerAdvisingNoteComment
  } else if (includes(['appointment', 'eForm'], props.parent.type)) {
    update = updateComment
  } else {
    update = updateNoteComment
  }
  return update(
    id,
    body,
    attachments,
    deleteAttachmentIds
  ).then(() => {
    editingComment.value = null
    alertScreenReader('updated comment')
    putFocusNextTick(`${idPrefix.value}-comment-${id}-edit-btn`)
  })
}
</script>

<style scoped>
.academic-timeline-column-date{
  margin-right: -24px;
}
.note-comments :deep(ul), .note-comments :deep(ol) {
  padding-left: 25px;
}
</style>
