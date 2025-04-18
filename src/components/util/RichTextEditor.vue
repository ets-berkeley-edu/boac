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
import {nextTick, onBeforeUnmount, onMounted, ref} from 'vue'

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

const ckElementId = ref('rich-text-editor')
const domFixAttemptCount = ref(0)
const domFixer = ref(undefined)
const editorLinkEventController = new AbortController()
const isInModal = ref(false)
const popupButtonEventController = new AbortController()
const popupFixer = ref(undefined)
const toolbarButtonEventController = new AbortController()
const toolbarLinkButtonEventController = new AbortController()
const tooltipRepositioner = ref(undefined)

onBeforeUnmount(() => {
  clearInterval(domFixer.value)
  clearInterval(popupFixer.value)
  clearInterval(tooltipRepositioner.value)
  editorLinkEventController.abort()
  popupButtonEventController.abort()
  toolbarButtonEventController.abort()
  toolbarLinkButtonEventController.abort()
})

onMounted(() => {
  ckElementId.value = `rich-text-editor-${new Date().getTime()}`
  nextTick(() => {
    // Is this instance inside a modal dialog?
    isInModal.value = !!document.querySelector(`.v-overlay-container #${ckElementId.value}`)
    initDomFixer()
  })
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
  const editor = document.getElementById(ckElementId.value)
  if (!editor) return abandonAttempt()
  const toolbar = editor.querySelector('.ck-editor__top')
  if (!toolbar) return abandonAttempt()
  const popupsContainer = document.body.querySelector('.ck.ck-reset_all.ck-body.ck-rounded-corners')
  if (!popupsContainer) return abandonAttempt()
  const toolbarButtons = toolbar.querySelectorAll('button')
  const linksInText = editor.querySelectorAll('[role="textbox"] a')
  each(linksInText, link => {
    link.addEventListener(
      'click',
      () => makePopupAccessible(popupsContainer, toolbar),
      {signal: editorLinkEventController.signal}
    )
  })
  if (isInModal.value) {
    // When embedded in a modal, the CKEditor toolbar popups are unreachable because they are attached to
    // the end of the DOM and outside the modal. We must move these "ck" elements. The user should not notice.
    toolbar.insertAdjacentElement('afterend', popupsContainer)
    each(toolbarButtons, button => {
      const buttonImage = button.querySelector('.ck-icon')
      if (buttonImage) {
        buttonImage.setAttribute('aria-hidden', 'true')
      }
      button.setAttribute('tabindex', 0)
      if ('Link' === button.textContent) {
        button.addEventListener(
          'click',
          () => makePopupAccessible(popupsContainer, toolbar),
          {signal: toolbarLinkButtonEventController.signal}
        )
      }
      button.addEventListener(
        'mouseenter',
        () => {
          correctTooltipPosition(popupsContainer, toolbar)
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
      if ('Link' === button.textContent) {
        button.addEventListener(
          'click',
          () => makePopupAccessible(popupsContainer, toolbar),
          {signal: toolbarLinkButtonEventController.signal}
        )
      }
    })
    clearInterval(domFixer.value)
  }
}

const correctPopupPosition = (popup, popupsContainer, toolbar) => {
  const offset = parseInt(popup.style.top, 10) - (toolbar.clientHeight + popup.clientHeight)
  const popupButtons = popup.querySelectorAll('button')
  popup.style.transform = `translateY(-${offset}px)`
  each(popupButtons, b => {
    b.addEventListener('mouseenter', () => {
      correctTooltipPosition(popupsContainer, toolbar)
      popupButtonEventController.abort()
    }, {signal: popupButtonEventController.signal})
  })
}

const correctTooltipPosition = (popupsContainer, toolbar) => {
  let attemptCount = 0
  tooltipRepositioner.value = setInterval(() => {
    if (attemptCount >= 10) {
      clearInterval(tooltipRepositioner.value)
    }
    const tooltip = popupsContainer.querySelector('.ck.ck-balloon-panel.ck-balloon-panel_with-arrow.ck-tooltip')
    attemptCount++
    if (tooltip) {
      const offset = parseInt(tooltip.style.top, 10) - toolbar.clientHeight
      tooltip.style.transform = `translateY(-${offset}px)`
      clearInterval(tooltipRepositioner.value)
    }
  }, 500)
}

const initDomFixer = () => {
  domFixAttemptCount.value = 0
  domFixer.value = setInterval(correctTheDOM, 500)
}

const makePopupAccessible = (popupsContainer, toolbar) => {
  let attemptCount = 0
  popupFixer.value = setInterval(() => {
    if (attemptCount >= 10) {
      clearInterval(popupFixer.value)
    }
    const popup = popupsContainer.querySelector('.ck.ck-balloon-panel.ck-balloon-panel_with-arrow:not(.ck-tooltip)')
    attemptCount++
    if (popup) {
      popup.setAttribute('aria-label', 'Create or edit link')
      popup.setAttribute('role', 'dialog')
      popup.setAttribute('aria-modal', 'true')
      if (isInModal.value) {
        correctPopupPosition(popup, popupsContainer, toolbar)
      }
      clearInterval(popupFixer.value)
    }
  }, 500)
}

const onUpdate = event => {
  props.onValueUpdate(isString(event) ? event : event.target.value)
}
</script>

<style>
.ck.ck-balloon-panel.ck-balloon-panel_with-arrow:not(.ck-tooltip) {
  /* make sure the Link popup doesn't cover its own tooltips */
  z-index: 9998 !important;
}
.ck-content ul {
  padding-left: 25px !important;
}
.ck-content ol {
  padding-left: 25px !important;
}
.ck.ck-sticky-panel .ck-sticky-panel__content_sticky {
  position: static !important;
}
</style>

<style>
@import "@/assets/styles/ckeditor-custom.css";
</style>
