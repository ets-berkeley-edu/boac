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
import {nextTick, onBeforeUnmount, onMounted, ref, watch} from 'vue'

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
  isInModal: { // @TODO - Creating links will break if this is false. Let's look into this more and see if we can implement it better.
    required: true,
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

const ckElementId = `rich-text-editor-${new Date().getTime()}`
const domFixAttemptCount = ref(0)
const domFixer = ref(undefined)
const popupButtonEventController = new AbortController()
const toolbarButtonEventController = new AbortController()
const toolbarLinkButtonEventController = new AbortController()
const tooltipRepositioner = ref(undefined)

watch(() => props.isInModal, () => {
  initDomFixer()
})

onBeforeUnmount(() => {
  clearInterval(domFixer.value)
  clearInterval(tooltipRepositioner.value)
  popupButtonEventController.abort()
  toolbarButtonEventController.abort()
  toolbarLinkButtonEventController.abort()
})

onMounted(() => {
  initDomFixer()
})

const abandonAttempt = () => {
  domFixAttemptCount.value++
  return false
}
const correctTheDOM = () => {
  if (domFixAttemptCount.value >= 10) {
    // Abort after N tries.
    clearInterval(domFixer.value)
    return false
  }
  const editor = document.getElementById(ckElementId)
  if (!editor) return abandonAttempt()
  const toolbar = editor.querySelector('.ck-editor__top')
  if (!toolbar) return abandonAttempt()
  const toolbarButtons = toolbar.querySelectorAll('button')
  if (props.isInModal) {
    // When embedded in a modal, the CKEditor toolbar popups are unreachable because they are attached to
    // the end of the DOM and outside the modal. We must move these "ck" elements. The user should not notice.
    const popupsContainer = document.body.querySelector('.ck.ck-reset_all.ck-body.ck-rounded-corners')
    if (!popupsContainer) return abandonAttempt()
    toolbar.insertAdjacentElement('afterend', popupsContainer)
    each(toolbarButtons, button => {
      button.setAttribute('tabindex', 0)
      if ('Link' === button.textContent) {
        button.addEventListener(
          'click',
          () => correctPopupPosition(editor, toolbar),
          {signal: toolbarLinkButtonEventController.signal}
        )
      }
      button.addEventListener(
        'mouseenter',
        () => {
          correctTooltipPosition(editor, toolbar)
          toolbarButtonEventController.abort()
        },
        {signal: toolbarButtonEventController.signal}
      )
    })
    clearInterval(domFixer.value)
  } else {
    // We're not in a modal.
    each(toolbarButtons, button => {
      button.setAttribute('tabindex', 0)
    })
    clearInterval(domFixer.value)
  }
}

const correctPopupPosition = (editor, toolbar) => {
  nextTick(() => {
    const popup = editor.querySelector('.ck.ck-balloon-panel.ck-balloon-panel_with-arrow:not(.ck-tooltip)')
    if (popup) {
      const offset = parseInt(popup.style.top, 10) - (toolbar.clientHeight + popup.clientHeight)
      const popupButtons = popup.querySelectorAll('button')
      popup.style.transform = `translateY(-${offset}px)`
      each(popupButtons, b => {
        b.addEventListener('mouseenter', () => {
          correctTooltipPosition(editor, toolbar)
          popupButtonEventController.abort()
        }, {signal: popupButtonEventController.signal})
      })
    }
  })
}

const correctTooltipPosition = (editor, toolbar) => {
  let attemptCount = 0
  tooltipRepositioner.value = setInterval(() => {
    if (attemptCount >= 10) {
      clearInterval(tooltipRepositioner.value)
    }
    const tooltip = editor.querySelector('.ck.ck-balloon-panel.ck-balloon-panel_with-arrow.ck-tooltip')
    if (tooltip) {
      const offset = parseInt(tooltip.style.top, 10) - toolbar.clientHeight
      tooltip.style.transform = `translateY(-${offset}px)`
      clearInterval(tooltipRepositioner.value)
    } else {
      attemptCount++
    }

  }, 500)
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

<style>
@import "@/assets/styles/ckeditor-custom.css";
</style>
