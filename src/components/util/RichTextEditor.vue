<template>
  <div>
    <label
      :id="`${ckElementId}-label`"
      :for="`${ckElementId}-textbox`"
      class="font-size-16 font-weight-bold"
    >
      {{ label }}
    </label>
    <span v-if="showAdvisingNoteBestPractices" class="font-size-14 font-weight-500 pl-2">
      <span :aria-hidden="true">(</span>
      <a
        id="link-to-advising-note-best-practices"
        href="https://advisingmatters.berkeley.edu/resources/shared-advising-notes"
        target="_blank"
        aria-label="Shared advising note best practices (opens in new tab)"
      >Shared advising note best practices<v-icon :icon="mdiOpenInNew" class="pl-1" /></a>
      <span :aria-hidden="true">)</span>
    </span>
    <div
      :id="ckElementId"
      aria-details="link-to-advising-note-best-practices"
      class="mt-2"
      :class="{'error': isInvalid}"
    >
      <ckeditor
        :model-value="initialValue"
        :disabled="disabled"
        :editor="ClassicEditor"
        :config="config"
        @input="onEditorInput"
        @ready="onEditorReady"
      />
    </div>
  </div>
</template>

<script setup>
import {AutoLink, Bold, ClassicEditor, ContextualBalloon, Essentials, Italic, Link, List, Paragraph, StandardEditingMode, TextTransformation, Typing} from 'ckeditor5'
import {each, isString} from 'lodash'
import {mdiOpenInNew} from '@mdi/js'
import {nextTick, onBeforeUnmount, onMounted, onUpdated, ref} from 'vue'
import {BoldCustom, ItalicCustom, ListBulletedCustom, ListNumberedCustom} from '@/plugins/ckeditor'

const props = defineProps({
  autoFocus: {
    required: false,
    type: Boolean
  },
  disabled: {
    required: false,
    type: Boolean
  },
  initialValue: {
    required: true,
    type: String
  },
  isInvalid: {
    required: false,
    type: Boolean
  },
  label: {
    required: true,
    type: String
  },
  onTogglePopover: {
    default: () => {},
    required: false,
    type: Function
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
const config = {
  licenseKey: 'GPL',
  link: {
    addTargetToExternalLinks: true
  },
  plugins: [AutoLink, Bold, BoldCustom, ContextualBalloon, Essentials, Italic, ItalicCustom, Link, List, ListBulletedCustom, ListNumberedCustom, Paragraph, StandardEditingMode, TextTransformation, Typing],
  toolbar: {
    items: ['boldCustom', 'italicCustom', 'listBulletedCustom', 'listNumberedCustom', 'link'],
    shouldNotGroupWhenFull: true
  },
  typing: {
    transformations: {
      remove: ['oneForth', 'oneHalf', 'oneThird', 'threeQuarters', 'twoThirds']
    }
  }
}
const domFixAttemptCount = ref(0)
const domFixer = ref(undefined)
const editor = ref()
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
  })
})

onUpdated(() => {
  if (props.isInvalid && props.autoFocus) {
    editor.value.focus()
  }
})

const abandonAttempt = () => {
  domFixAttemptCount.value++
  return false
}

const correctAttributes = (toolbar) => {
  const textbox = editor.value.ui.view.editable.element
  if (textbox) {
    textbox.setAttribute('aria-multiline', true)
    textbox.setAttribute('id', `${ckElementId.value}-textbox`)
  }
  toolbar.setAttribute('aria-label', `${props.label} editor`)
  toolbar.setAttribute('aria-controls', `${ckElementId.value}-textbox`)
  toolbar.setAttribute('tabindex', 0)
}

const correctTheDOM = () => {
  if (domFixAttemptCount.value >= 5) {
    // Abort after N tries.
    clearInterval(domFixer.value)
    return false
  }
  const toolbar = editor.value.ui.view.element.querySelector('[role="toolbar"]')
  if (!toolbar) return abandonAttempt()
  correctAttributes(toolbar)

  const popupsContainer = document.body.querySelector('.ck.ck-reset_all.ck-body.ck-rounded-corners')
  if (!popupsContainer) return abandonAttempt()
  const toolbarButtons = toolbar.querySelectorAll('button')
  const linksInText = editor.value.ui.view.editable.element.querySelectorAll('a')
  each(linksInText, link => {
    link.addEventListener(
      'click',
      () => makePopupAccessible(popupsContainer, toolbar, 'Edit link'),
      {signal: editorLinkEventController.signal}
    )
  })
  if (isInModal.value) {
    // When embedded in a modal, the CKEditor toolbar popups are unreachable because they are attached to
    // the end of the DOM and outside the modal. We must move these "ck" elements. The user should not notice.
    toolbar.insertAdjacentElement('afterend', popupsContainer)
  }
  each(toolbarButtons, button => {
    const buttonImage = button.querySelector('.ck-icon')
    if (buttonImage) {
      buttonImage.setAttribute('aria-hidden', true)
    }
    if ('Link' === button.textContent) {
      button.addEventListener(
        'click',
        () => makePopupAccessible(popupsContainer, toolbar, 'Create link'),
        {signal: toolbarLinkButtonEventController.signal}
      )
    } else {
      button.addEventListener(
        'click',
        onButtonClick,
      )
    }
    if (isInModal.value) {
      button.addEventListener(
        'mouseenter',
        () => {
          correctTooltipPosition(popupsContainer, toolbar)
          toolbarButtonEventController.abort()
        },
        {signal: toolbarButtonEventController.signal}
      )
    }
  })
  clearInterval(domFixer.value)
}

const onButtonClick = e => {
  // If the button was pressed using a mouse or equivalent pointing device, move focus back to the textbox.
  // Otherwise, the button was pressed using the keyboard and focus will stay on the button.
  if (e.pointerType) {
    editor.value.editing.view.focus()
  }
}

const correctPopupPosition = (popup, popupsContainer, toolbar) => {
  const offset = parseInt(popup.style.top, 10) - (toolbar.clientHeight + popup.clientHeight)
  const popupButtons = popup.querySelectorAll(':where(button, a)')
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

const makePopupAccessible = (popupsContainer, toolbar, ariaLabel) => {
  let attemptCount = 0
  popupFixer.value = setInterval(() => {
    if (attemptCount >= 10) {
      clearInterval(popupFixer.value)
    }
    const popup = popupsContainer.querySelector('.ck.ck-balloon-panel.ck-balloon-panel_with-arrow:not(.ck-tooltip)')
    attemptCount++
    if (popup) {
      popup.setAttribute('aria-label', ariaLabel)
      popup.setAttribute('role', 'dialog')
      popup.setAttribute('aria-modal', 'true')
      if (isInModal.value) {
        correctPopupPosition(popup, popupsContainer, toolbar)
      }
      clearInterval(popupFixer.value)
    }
  }, 500)
}

const manageToolbarFocus = () => {
  let lastFocusedButton

  // When focus leaves the editor UI entirely, reset so Bold is the first focused button
  editor.value.ui.focusTracker.on('change:isFocused', (e, data, isFocused) => {
    if (!isFocused) {
      lastFocusedButton = null
    }
  })
  editor.value.ui.view.toolbar.focusTracker.on('change:focusedElement', e => {
    const focusedElement = editor.value.ui.view.toolbar.focusTracker.focusedElement
    if (focusedElement && 'button' === focusedElement.type && focusedElement !== lastFocusedButton) {
      // Focus is landing on a toolbar button from another toolbar button or from the toolbar itself
      lastFocusedButton = focusedElement
      lastFocusedButton.focus()
      editor.value.ui.view.toolbar.element.setAttribute('tabindex', '-1')
    } else if (focusedElement) {
      // Focus is landing on the toolbar itself from outside of the toolbar. When focus lands on the toolbar,
      // we move it either to the previously focused button or the first button.
      editor.value.ui.view.toolbar.element.setAttribute('tabindex', '-1')
      if (!lastFocusedButton) {
        lastFocusedButton = editor.value.ui.view.toolbar.focusTracker.elements[1]
      }
      lastFocusedButton.focus()
    } else {
      // Focus is leaving the toolbar
      editor.value.ui.view.toolbar.element.setAttribute('tabindex', '0')
    }
    e.stop()
    return false
  })
}

const onChangePopoverVisible = (e, propertyName, newValue) => {
  props.onTogglePopover(newValue)
}

const onEditorInput = event => {
  props.onValueUpdate(isString(event) ? event : event.target.value)
}

const onEditorReady = editorInstance => {
  editor.value = editorInstance
  initDomFixer()
  registerPopupListener()
  manageToolbarFocus()
  if (props.autoFocus) {
    editor.value.focus()
  }
}

const registerPopupListener = () => {
  const balloonInstance = editor.value.plugins.get('ContextualBalloon')
  const balloonPanelView = balloonInstance.view
  balloonPanelView.off('change:isVisible', onChangePopoverVisible)
  balloonPanelView.on('change:isVisible', onChangePopoverVisible)
}
</script>

<style>
.ck.ck-balloon-panel.ck-balloon-panel_with-arrow:not(.ck-tooltip) {
  /* make sure the Link popup doesn't cover its own tooltips */
  z-index: 9998 !important;
}
.ck.ck-balloon-panel .ck-link-actions__preview {
  font-size: 1rem;
}
.ck.ck-balloon-panel.ck-powered-by-balloon {
  display: none !important;
}
.ck.ck-content.ck-editor__editable.ck-focused:not(.ck-editor__nested-editable) {
  border-style: solid !important;
  border-width: 1px !important;
  box-shadow: none !important;
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
.ck.ck-sticky-panel__content:focus-within,
.ck.ck-editor:hover {
  --ck-color-base-border: hsla(0, 0%, 0%, 1) !important;
  transition: border-color 250ms cubic-bezier(0.4, 0, 0.2, 1);
}
.ck.ck-content.ck-editor__editable {
  border-radius: 4px;
  border-style: solid !important;
  border-width: 1 !important;
  height: 180px;
  &.text-error input {
    color: rgb(var(--v-theme-error))
  }
}
.error .ck.ck-editor:not(:has(.ck.ck-toolbar:focus-within)) .ck.ck-editor__editable {
  border-color: rgba(var(--v-theme-error)) !important;
  &.ck-focused {
    outline-color: rgba(var(--v-theme-error)) !important;
  }
}
</style>
