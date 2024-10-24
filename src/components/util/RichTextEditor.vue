<template>
  <div>
    <label
      :id="`${ckElementId}-label`"
      :for="ckElementId"
      class="font-size-16 font-weight-bold"
    >
      {{ label }}
      <span v-if="showAdvisingNoteBestPractices" class="font-size-14 font-weight-500">
        (<a
          id="link-to-advising-note-best-practices"
          href="https://advisingmatters.berkeley.edu/resources/shared-advising-notes"
          target="_blank"
          aria-label="Shared advising note best practices (opens in new window)"
        >Shared advising note best practices<v-icon :icon="mdiOpenInNew" class="pl-1" /></a>)
      </span>
    </label>
    <div
      :id="ckElementId"
      aria-details="link-to-advising-note-best-practices"
      :aria-labelledby="`${ckElementId}-label`"
      class="mt-2"
      role="textbox"
    >
      <ckeditor
        :model-value="initialValue"
        :disabled="disabled"
        :editor="ClassicEditor"
        :config="editorConfig"
        @input="onUpdate"
      />
    </div>
  </div>
</template>

<script setup>
import ClassicEditor from '@ckeditor/ckeditor5-build-classic'
import {each, isString} from 'lodash'
import {mdiOpenInNew} from '@mdi/js'
import {onMounted, ref, watch} from 'vue'

const props = defineProps({
  disabled: {
    required: false,
    type: Boolean
  },
  editorConfig: {
    required: false,
    default: () => ({
      link: {
        addTargetToExternalLinks: true
      },
      toolbar: ['bold', 'italic', 'bulletedList', 'numberedList', 'link'],
      typing: {
        transformations: {
          remove: ['oneForth', 'oneHalf', 'oneThird', 'threeQuarters', 'twoThirds']
        }
      }
    }),
    type: Object
  },
  initialValue: {
    required: true,
    type: String
  },
  isInModal: {
    required: false,
    type: Boolean
  },
  label: {
    required: true,
    type: String
  },
  onValueUpdate: {
    required: true,
    type: Function
  },
  showAdvisingNoteBestPractices: {
    required: false,
    type: Boolean
  }
})

const domFixAttemptCount = ref(0)
const domFixer = ref(undefined)
const ckElementId = `rich-text-editor-${new Date().getTime()}`

watch(() => props.isInModal, () => {
  initDomFixer()
})

onMounted(() => {
  initDomFixer()
})

const correctTheDOM = () => {
  if (domFixAttemptCount.value === 10) {
    // Abort after N tries.
    clearInterval(domFixer.value)
  } else if (props.isInModal) {
    // When embedded in a modal, the CKEditor toolbar elements are unreachable because they are attached to
    // the end of the DOM and outside the modal. We must move these "ck" elements. The user should not notice.
    const ckEditorTool = 'ck ck-reset ck-editor ck-rounded-corners'
    const elements = document.getElementsByClassName(ckEditorTool)
    if (elements.length > 0) {
      each(elements, element => {
        document.getElementById(ckElementId).appendChild(element)
      })
      clearInterval(domFixer.value)
    } else {
      domFixAttemptCount.value++
    }
  } else {
    // We're not in a modal.
    clearInterval(domFixer.value)
  }
}

const initDomFixer = () => {
  domFixAttemptCount.value = 0
  domFixer.value = setInterval(correctTheDOM, 500)
}

const onUpdate = event => {
  props.onValueUpdate(isString(event) ? event : event.target.value)
}
</script>

<style scoped>
:deep(.ck-content ul) {
  padding-left: 25px !important;
}
:deep(.ck-content ol) {
  padding-left: 25px !important;
}
:deep(.ck.ck-sticky-panel .ck-sticky-panel__content_sticky) {
  position: static !important;
}
</style>
