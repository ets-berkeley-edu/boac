<template>
  <section class="note-comments">
    <h4 class="text-medium-emphasis mb-2">Comments</h4>
    <article
      v-for="comment in note.comments"
      :key="comment.id"
      class="border-b-sm d-flex justify-space-between py-4 my-2"
    >
      <div>
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
      <footer class="column-date">
        <v-btn
          :id="`note-${note.id}-comment-${comment.id}-edit-btn`"
          class="mb-2"
          color="primary"
          density="compact"
          text="Edit Comment"
          variant="text"
        />
        <div class="text-medium-emphasis">Replied:</div>
        <div>Dec 18, 2023 @ 3:08PM</div>
      </footer>
    </article>
    <v-btn
      v-if="!isCreatingComment"
      :id="`note-${note.id}-add-comment-btn`"
      class="bg-white my-2"
      color="primary"
      :prepend-icon="mdiPlus"
      text="Add Comment"
      variant="outlined"
      @click="onClickAddComment"
    />
    <div v-if="isCreatingComment">
      <RichTextEditor
        :id="`note-${note.id}-comment-text`"
        :disabled="isSaving"
        :initial-value="commentText"
        label="Add Comment"
        :on-value-update="v => commentText = v"
      />
      <AdvisingNoteAttachments
        :add="addAttachments"
        :attachments="commentAttachments || []"
        class="attachments-edit py-3"
        :disabled="isUpdatingAttachments"
        :id-prefix="`note-${note.id}`"
        :is-downloadable="true"
        :note="note"
        :remove="removeAttachmentByIndex"
      />
      <div class="d-flex pt-2">
        <ProgressButton
          :id="`note-${note.id}-save-comment-btn`"
          :action="onClickSave"
          :disabled="isSaving || isUpdatingAttachments"
          class="mr-2"
          color="primary"
          :in-progress="isSaving"
          text="Save"
        />
        <v-btn
          :id="`note-${note.id}-cancel-comment-btn`"
          color="primary"
          text="Cancel"
          variant="text"
          @click="onClickCancel"
        />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import {mdiInformation, mdiPlus} from '@mdi/js'
import {ref} from 'vue'
import AdvisingNoteAttachments from '@/components/note/AdvisingNoteAttachments'
import ProgressButton from '@/components/util/ProgressButton'
import RichTextEditor from '@/components/util/RichTextEditor'
import {putFocusNextTick} from '@/lib/utils'

const props = defineProps({
  note: {
    required: true,
    type: Object
  }
})

const commentText = ref('')
const commentAttachments = ref([])
const isCreatingComment = ref(false)
const isSaving = ref(false)
const isUpdatingAttachments = ref(false)

const addAttachments = () => {
  // TODO: add attachment
}
const onClickAddComment = () => {
  isCreatingComment.value = true
  putFocusNextTick(`note-${props.note.id}-comment-text`)
}
const onClickCancel = () => {
  isCreatingComment.value = false
  putFocusNextTick(`note-${props.note.id}-add-comment-btn`)
}
const onClickSave = () => {
  // TODO: save
  isCreatingComment.value = false
}
const removeAttachmentByIndex = () => {
  // TODO: remove attachment
}
</script>

<style scoped>
.note-comments {
  margin-right: -9rem;
}
</style>
