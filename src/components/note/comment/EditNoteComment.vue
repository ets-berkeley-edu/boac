<template>
  <div class="flex-grow-1">
    <RichTextEditor
      :id="`${idPrefix}-text`"
      :disabled="isSaving"
      :initial-value="commentText"
      :label="`${comment ? 'Edit' : 'Add'} Comment`"
      :on-value-update="v => commentText = v"
    />
    <AdvisingNoteAttachments
      :add="addCommentAttachments"
      :attachments="commentAttachments"
      class="attachments-edit py-3"
      :disabled="isSaving || isUpdatingAttachments"
      :id-prefix="idPrefix"
      :is-downloadable="true"
      :note="note"
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
import {get} from 'lodash'
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
  note: {
    required: true,
    type: Object
  },
  save: {
    required: true,
    type: Function
  }
})

const commentAttachments = ref([])
const commentText = ref('')
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
  isSaving.value = true
  props.save(
    commentText,
    commentAttachments,
    get(props.comment, 'id')
  ).then(() => isSaving.value = false)
}

const removeAttachmentByIndex = index => {
  const attachment = commentAttachments.value[index]
  commentAttachments.value.splice(index, 1)
  alertScreenReader(`Removed attachment '${attachment.displayName}'`)
}
</script>
