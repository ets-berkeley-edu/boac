<template>
  <div>
    <RichTextEditor
      :id="`${idPrefix}-text`"
      :auto-focus="true"
      :disabled="isSaving"
      :initial-value="commentText"
      :is-invalid="!!error"
      :label="`${comment ? 'Edit' : 'Add'} Comment`"
      :on-value-update="onInputText"
    />
    <div aria-live="polite">
      <v-alert
        v-if="error"
        id="edit-comment-input-error"
        class="font-size-14 line-height-normal"
        density="compact"
        role="none"
        :text="error"
        type="error"
        variant="tonal"
      />
    </div>
    <AdvisingNoteAttachments
      :add="addCommentAttachments"
      :attachments="commentAttachments"
      class="attachments-edit py-3"
      :disabled="isSaving || isUpdatingAttachments"
      :id-prefix="idPrefix"
      :is-downloadable="!isSaving"
      :note="comment || {parentNoteId: parentNoteId}"
      :remove="removeAttachmentByIndex"
    />
    <div class="d-flex pt-2">
      <ProgressButton
        :id="`${idPrefix}-save-btn`"
        :action="onClickSave"
        :disabled="isSaving || isUpdatingAttachments"
        class="mr-2"
        color="primary"
        :in-progress="isSaving"
        text="Save"
      />
      <v-btn
        :id="`${idPrefix}-cancel-btn`"
        color="primary"
        text="Cancel"
        variant="text"
        @click="onClickCancel"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import {get, isEmpty, trim} from 'lodash'
import {onMounted, ref} from 'vue'
import AdvisingNoteAttachments from '@/components/note/AdvisingNoteAttachments'
import ProgressButton from '@/components/util/ProgressButton'
import RichTextEditor from '@/components/util/RichTextEditor'
import {alertScreenReader} from '@/lib/utils'

const props = defineProps({
  cancel: {
    required: true,
    type: Function
  },
  comment: {
    default: undefined,
    required: false,
    type: Object
  },
  idPrefix: {
    required: true,
    type: String
  },
  parentNoteId: {
    default: undefined,
    required: false,
    type: String
  },
  save: {
    required: true,
    type: Function
  }
})

const commentAttachments = ref([])
const commentText = ref('')
const deleteAttachmentIds = ref([])
const error = ref()
const isSaving = ref(false)
const isUpdatingAttachments = ref(false)

onMounted(() => {
  if (props.comment) {
    commentAttachments.value = props.comment.attachments
    commentText.value = props.comment.body
  }
})

const addCommentAttachments = attachments => {
  isUpdatingAttachments.value = true
  return new Promise(resolve => {
    commentAttachments.value = commentAttachments.value.concat(attachments)
    isUpdatingAttachments.value = false
    resolve()
  })
}

const onClickCancel = () => {
  commentAttachments.value = []
  commentText.value = ''
  props.cancel()
}

const onClickSave = () => {
  const body = trim(commentText.value)
  if (isEmpty(body)) {
    error.value = 'Comment cannot be empty.'
  } else {
    isSaving.value = true
    props.save(
      get(props.comment, 'id'),
      trim(commentText.value),
      commentAttachments.value,
      deleteAttachmentIds.value
    ).then(() => isSaving.value = false)
  }
}

const onInputText = text => {
  commentText.value = text
  if (error.value) {
    error.value = null
  }
}

const removeAttachmentByIndex = index => {
  const attachment = commentAttachments.value[index]
  deleteAttachmentIds.value.push(attachment.id)
  commentAttachments.value.splice(index, 1)
  alertScreenReader(`Removed attachment '${attachment.displayName}'`)
}
</script>
