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
    <!-- With tagging on, this wrapper is the positioning context for the tag dropdown, which renders inside it (not on
    <body>) so it stays within a note modal's DOM and focus lock. -->
    <div
      :id="ckElementId"
      ref="editorWrapper"
      aria-details="link-to-advising-note-best-practices"
      class="mt-2"
      :class="{'error': isInvalid, 'position-relative': enableUserTags}"
    >
      <!-- No reload guard is needed on this binding: with tagging on, the editor emits "@<UID>" bodies (UserTagData),
      which is exactly what parents store and pass back, so an echoed value matches what the editor already holds. -->
      <ckeditor
        :model-value="initialValue"
        :disabled="disabled"
        :editor="ClassicEditor"
        :config="config"
        @input="onEditorInput"
        @ready="onEditorReady"
      />
      <UserTagDropdown
        v-if="tagIsVisible"
        :id="tagListboxId"
        :highlighted-index="tagHighlightedIndex"
        :is-loading="tagIsLoading"
        :message="tagMessage"
        :position="tagPosition"
        :typed-text="tagTypedText"
        :users="tagUsers"
        @select="commitTag"
      />
    </div>
  </div>
</template>

<script setup>
import {AutoLink, Bold, ClassicEditor, ContextualBalloon, Essentials, Italic, Link, List, Mention, Paragraph, StandardEditingMode, TextTransformation, Typing} from 'ckeditor5'
import {compact, debounce, each, get, isString} from 'lodash'
import {mdiOpenInNew} from '@mdi/js'
import {nextTick, onBeforeUnmount, onMounted, onUpdated, ref, toRaw, watch} from 'vue'
import UserTagDropdown from '@/components/util/UserTagDropdown'
import {alertScreenReader} from '@/lib/utils'
import {BoldCustom, ItalicCustom, ListBulletedCustom, ListNumberedCustom, MentionUid, UserTagData, attachUserTagAutocomplete, insertUserTag, isUserTagRangeCurrent} from '@/plugins/ckeditor'
import {findTaggableUsers} from '@/api/user-tags'
import {UNKNOWN_USER_NAME, nextUserTagListboxId, optionId} from '@/lib/user-tags'

const props = defineProps({
  autoFocus: {
    required: false,
    type: Boolean
  },
  disabled: {
    required: false,
    type: Boolean
  },
  // Turns on user tagging: the "@" autocomplete, and the "@<UID>" storage format. With it on, the editor shows each tag as
  // a name but emits (and expects back) bodies with tags as plain "@<UID>". Read once at setup, since the plugin list is
  // fixed then.
  enableUserTags: {
    required: false,
    type: Boolean
  },
  initialValue: {
    default: '',
    required: false,
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
  },
  // A TaggedUsers map (see src/lib/types.ts) from the note's API response: the trusted name for each UID tagged in the
  // body, or null for a tag whose name is unknown. The editor shows these names in place of the stored "@<UID>" text.
  taggedUsers: {
    default: null,
    required: false,
    type: Object
  },
  // A TagContext (see src/lib/types.ts): what the author is writing, so the server knows who may be tagged there.
  // It's read at each lookup, so changes to privacy or the recipient count take effect while the editor is open.
  userTagContext: {
    default: null,
    required: false,
    type: Object
  }
})

const ckElementId = ref('rich-text-editor')

// Names of people tagged in this editor session, by UID. It's per instance and outlives the dropdown, so a tag picked
// here keeps its name even though it isn't in taggedUsers until the note is saved and reloaded. Not reactive: only the
// CKEditor plugins read it, through nameFor.
const pickedTagNames = new Map()

// The name lookup MentionUid and UserTagData read from config.userTags. Returns the name, null for a tag with no known
// name, or undefined for a UID nobody tagged (which stays plain text). It reads props.taggedUsers on every call, so a
// parent's updated map is used without rebuilding the editor.
const nameFor = uid => {
  if (pickedTagNames.has(uid)) {
    return pickedTagNames.get(uid)
  }
  const taggedUsers = props.taggedUsers
  if (taggedUsers && Object.prototype.hasOwnProperty.call(taggedUsers, uid)) {
    const taggedUser = taggedUsers[uid]
    // An empty name counts as unknown, so the tag reads "@Unknown user" rather than a bare "@".
    return taggedUser?.name || null
  }
  return undefined
}

const config = {
  licenseKey: 'GPL',
  link: {
    addTargetToExternalLinks: true
  },
  plugins: [
    AutoLink, Bold, BoldCustom, ContextualBalloon, Essentials, Italic, ItalicCustom, Link, List, ListBulletedCustom, ListNumberedCustom, Paragraph, StandardEditingMode, TextTransformation, Typing,
    // Mention (MentionEditing plus MentionUI) is loaded whole because MentionUid needs its public toMentionAttribute,
    // which only the Mention plugin offers. MentionUI stays inert: config.mention has no feeds, so it never opens its
    // dropdown, which lacks listbox ARIA. UserTagDropdown takes its place. MentionUid and UserTagData store each tag as
    // "@<UID>" while the editor shows the person's name.
    ...(props.enableUserTags ? [Mention, MentionUid, UserTagData] : [])
  ],
  // Only editors with tagging on get these keys, so every other editor's config is exactly as before.
  ...(props.enableUserTags ? {mention: {feeds: []}, userTags: {nameFor}} : {}),
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

// User tag ("@") autocomplete. The dropdown's text and keyboard handling are explained in user-tags.ts and the design doc.
const TAG_BATCH_MESSAGE = 'You can\'t tag people on notes to more than one student.'
const TAG_ERROR_MESSAGE = 'Couldn\'t load people. Keep typing to try again.'
// Space between the "@text" and the dropdown, in px.
const TAG_DROPDOWN_GAP = 4
// When the "@" sits near the editor's right edge, shift the dropdown left so it keeps at least this much width
// (in rem, so it grows with the text size) instead of wrapping into a narrow sliver.
const TAG_DROPDOWN_MIN_WIDTH_REM = 20
const editorWrapper = ref(null)
const tagHighlightedIndex = ref(0)
const tagIsLoading = ref(false)
const tagIsVisible = ref(false)
// Unique per editor instance; see nextUserTagListboxId.
const tagListboxId = nextUserTagListboxId()
const tagMessage = ref(null)
const tagPosition = ref({top: 0, left: 0})
const tagTypedText = ref('')
const tagUsers = ref([])
// CKEditor objects and the request controller stay out of Vue's reactivity: nothing renders them, and a reactive
// proxy around a CKEditor range would not be the object CKEditor expects back.
let detachUserTags = null
// Set when a re-render comes from the tag dropdown, so onUpdated skips its refocus. onUpdated refocuses the editor on
// every re-render while it's invalid with autoFocus (as in EditComment). When the author tabs or clicks out, the dropdown
// closes on blur, which re-renders; without this flag that render would pull focus straight back into the editor, a
// keyboard trap (WCAG 2.1.2).
let isTagRender = false
// Lookups are never cancelled: a slow server finishes the answer even after the author clicks away or keeps typing, and
// the cache below keeps it for when they come back. This counter marks which lookup the dropdown is waiting for, so a
// late answer for anything else is dropped.
let tagLookupToken = 0
let tagCaretRect = null
let tagRange = null

onBeforeUnmount(() => {
  if (detachUserTags) {
    detachUserTags()
  }
  lookupTaggableUsers.cancel()
  // Makes the "still the lookup we're waiting for" check drop an answer that arrives after unmount, so nothing is
  // announced for an editor that's gone.
  tagLookupToken++
  // Watchers stop on unmount, so the one that removes this listener won't run if the dropdown was open.
  window.removeEventListener('keydown', onTagEscapeKeyDown, {capture: true})
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
  // Skip renders caused by the tag dropdown: refocusing on those would trap keyboard users (see isTagRender).
  if (props.isInvalid && props.autoFocus && !isTagRender) {
    editor.value.focus()
  }
  isTagRender = false
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
      if (popup.querySelector('.ck-link-form')) {
        ensureLinkFormFocus()
      }
      clearInterval(popupFixer.value)
    }
  }, 500)
}
/**
 * The new version of ckeditor renders "Displayed text" puts focus first on link URL,
 * but we want it on the displayed text.
 */
const reorderLinkFormFocusables = formView => {
  const focusables = formView._focusables
  if (!focusables) {
    return
  }
  const ordered = [
    formView.displayedTextInputView,
    formView.urlInputView,
    formView.saveButtonView,
    ...formView.providersListChildren,
    formView.backButtonView
  ].filter(Boolean)
  if (focusables.get(0) === formView.displayedTextInputView) {
    return
  }
  focusables.clear()
  each(ordered, view => focusables.add(view))
}

const patchLinkFormFocus = formView => {
  if (!formView || formView._boaFocusPatched) {
    return
  }
  formView._boaFocusPatched = true
  reorderLinkFormFocusables(formView)
  formView.focus = () => {
    if (formView.displayedTextInputView.isEnabled) {
      formView.displayedTextInputView.focus()
    } else {
      formView.urlInputView.focus()
    }
  }
}

const ensureLinkFormFocus = () => {
  const linkUI = editor.value?.plugins.get('LinkUI')
  const formView = linkUI?.formView
  if (!formView) {
    return
  }
  patchLinkFormFocus(formView)
  requestAnimationFrame(() => {
    formView.focus()
  })
}

const configureLinkFormFocus = () => {
  const balloon = editor.value.plugins.get('ContextualBalloon')
  const linkUI = editor.value.plugins.get('LinkUI')
  if (!balloon || !linkUI) {
    return
  }
  balloon.on('change:visibleView', (evt, name, visibleView) => {
    if (visibleView && visibleView === linkUI.formView) {
      ensureLinkFormFocus()
    }
  })
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
  configureLinkFormFocus()
  manageToolbarFocus()
  if (props.enableUserTags) {
    // Pass the raw editor: the glue keeps it, and a reactive proxy would hand CKEditor wrapped objects.
    detachUserTags = attachUserTagAutocomplete(editorInstance, {
      allowBareMarker: isBatchNote,
      hasOptions: hasTagOptions,
      isVisible: () => tagIsVisible.value,
      onClose: closeTagDropdown,
      onCommit: () => commitTag(tagUsers.value[tagHighlightedIndex.value]),
      onMatch: onTagMatch,
      onMove: moveTagHighlight
    })
  }
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

/* User tag ("@") autocomplete. user-tags.ts spots "@text" and handles the keys; this component owns the dropdown. */

// Describes the highlighted person, e.g. "<name>, <title>, <dept>, 2 of 5", leaving out whichever parts are missing.
// Both the results announcement and the move announcement use it, so they read the same way.
const describeTagHighlight = () => {
  const user = tagUsers.value[tagHighlightedIndex.value]
  const position = `${tagHighlightedIndex.value + 1} of ${tagUsers.value.length}`
  return compact([user.name, user.title, user.deptName, position]).join(', ')
}

const announceTagHighlight = () => {
  alertScreenReader(describeTagHighlight())
}

const closeTagDropdown = () => {
  // user-tags.ts reports a close on every blur and every "unmatched", so most calls find nothing open.
  if (!tagIsVisible.value) {
    return
  }
  lookupTaggableUsers.cancel()
  // Stop waiting for the answer, but let the request finish so its result is cached for the next time.
  tagLookupToken++
  tagCaretRect = null
  tagHighlightedIndex.value = 0
  tagIsLoading.value = false
  tagIsVisible.value = false
  tagMessage.value = null
  tagRange = null
  tagUsers.value = []
}

const commitTag = user => {
  const editorInstance = toRaw(editor.value)
  const range = tagRange
  const typedText = tagTypedText.value
  // Close first: inserting makes TextWatcher report "unmatched", and the dropdown should already be gone by then.
  closeTagDropdown()
  // If the "@text" changed since the dropdown opened (e.g. the author pressed undo), don't overwrite whatever is there now.
  if (user && range && isUserTagRangeCurrent(range, typedText)) {
    // Record the name before inserting: MentionUid's post-fixer runs during the insert and rewrites any tag whose text
    // doesn't match nameFor, so the picked name must already be known by then.
    pickedTagNames.set(user.uid, user.name || null)
    insertUserTag(editorInstance, range, user)
    alertScreenReader(`Tagged ${user.name || UNKNOWN_USER_NAME}`)
  }
}

// The dropdown is absolutely positioned in the editor wrapper, so it can only be seen within the nearest ancestor that
// clips or scrolls (e.g. a modal's body), and within the window.
const getVisibleBounds = element => {
  let top = 0
  let bottom = window.innerHeight
  for (let ancestor = element.parentElement; ancestor && ancestor !== document.body; ancestor = ancestor.parentElement) {
    if (window.getComputedStyle(ancestor).overflowY !== 'visible') {
      const rect = ancestor.getBoundingClientRect()
      top = Math.max(top, rect.top)
      bottom = Math.min(bottom, rect.bottom)
      break
    }
  }
  return {top, bottom}
}

const hasTagOptions = () => tagIsVisible.value && !tagIsLoading.value && !tagMessage.value && tagUsers.value.length > 0

const isBatchNote = () => get(props.userTagContext, 'recipientCount', 0) > 1

// Answers are kept for a minute, per context and typed text, so reopening the dropdown on the same "@text" (or retyping it
// after a click elsewhere) shows people at once. A minute is short enough that a change in who may be tagged shows up soon,
// and the save checks the tags again anyway.
const TAG_CACHE_MS = 60 * 1000
const TAG_CACHE_MAX_ENTRIES = 50
const tagSearchCache = new Map()

const searchTaggableUsers = typedText => {
  const context = props.userTagContext || {}
  const key = `${JSON.stringify(context)}|${typedText.trim().toLowerCase()}`
  const cached = tagSearchCache.get(key)
  if (cached && Date.now() - cached.at < TAG_CACHE_MS) {
    return cached.promise
  }
  if (tagSearchCache.size >= TAG_CACHE_MAX_ENTRIES) {
    tagSearchCache.clear()
  }
  const promise = findTaggableUsers(typedText, context)
  tagSearchCache.set(key, {at: Date.now(), promise})
  // A failed lookup must not be served again from the cache.
  promise.catch(() => tagSearchCache.delete(key))
  return promise
}

// Debounced so a lookup goes out only once the author pauses. A response is used only if it is for the lookup the dropdown is
// still waiting for, so a slow answer for "ab" can never replace the answer for "abc".
const lookupTaggableUsers = debounce(typedText => {
  const token = ++tagLookupToken
  searchTaggableUsers(typedText).then(users => {
    if (token !== tagLookupToken) {
      return
    }
    if (users.length) {
      tagIsLoading.value = false
      tagUsers.value = users
      tagHighlightedIndex.value = 0
      // Name the first person too, since they're highlighted already and Enter would pick them.
      const found = `${users.length === 1 ? '1 person' : `${users.length} people`} found`
      alertScreenReader(`${found}. ${describeTagHighlight()}. Use up and down arrows to choose.`)
    } else {
      showTagMessage(`No one you can tag matches '${typedText}'.`)
    }
  }).catch(() => {
    if (token !== tagLookupToken) {
      return
    }
    showTagMessage(TAG_ERROR_MESSAGE)
  })
}, 250)

const moveTagHighlight = delta => {
  const count = tagUsers.value.length
  // Wrap around at both ends.
  tagHighlightedIndex.value = (tagHighlightedIndex.value + delta + count) % count
  announceTagHighlight()
}

// The main note modal (EditBatchNoteModal) listens for Esc in the capture phase on the modal itself. Capture listeners
// on an ancestor run before CKEditor's keydown handling on the text box, so the Esc that should only dismiss the
// dropdown would also discard the note. A window capture listener runs before any element's, so while the dropdown is
// open we take that Esc here and stop it. The CKEditor-level Esc handling in user-tags.ts stays as a fallback.
const onTagEscapeKeyDown = event => {
  const hasModifier = event.shiftKey || event.ctrlKey || event.metaKey || event.altKey
  const editable = editor.value ? toRaw(editor.value).ui.view.editable.element : null
  if (event.key === 'Escape' && !hasModifier && editable && editable.contains(event.target)) {
    event.stopPropagation()
    event.preventDefault()
    closeTagDropdown()
  }
}

const onTagMatch = ({typedText, range, caretRect}) => {
  // The same "@text" can be reported again (e.g. a click that leaves the caret where it was, or Delete removing text
  // after the caret). Keep what's showing rather than re-searching and re-announcing.
  const isUnchanged = tagIsVisible.value && typedText === tagTypedText.value
  tagCaretRect = caretRect
  tagRange = range
  tagTypedText.value = typedText
  tagIsVisible.value = true
  nextTick(placeTagDropdown)
  if (isBatchNote()) {
    // Tags aren't allowed on a batch note, so explain that and send no request. Announce it once, not per keystroke.
    lookupTaggableUsers.cancel()
    tagLookupToken++
    if (tagMessage.value !== TAG_BATCH_MESSAGE) {
      showTagMessage(TAG_BATCH_MESSAGE)
    }
  } else if (!isUnchanged || tagMessage.value === TAG_BATCH_MESSAGE) {
    // Stop waiting for the older lookup now, not just when the debounced one fires, so its answer can't land during the wait.
    tagLookupToken++
    // Announce "Searching…" only when loading starts from a non-loading state: the dropdown just opened, or it was
    // showing results or a message row. While a search is already pending, more typing stays quiet, so fast typing
    // doesn't repeat it. The results are announced when they arrive.
    if (!tagIsLoading.value) {
      alertScreenReader('Searching…')
    }
    tagUsers.value = []
    tagHighlightedIndex.value = 0
    tagMessage.value = null
    tagIsLoading.value = true
    lookupTaggableUsers(typedText)
  }
}

// Places the dropdown just below the "@text", or above it if it fits better there. The rect spans from the "@" to the
// caret, so on a tag that wraps we go below its last line or above its first. Runs after each render, because the
// dropdown's height (and so whether it fits below) changes as "Searching…" turns into results.
const placeTagDropdown = () => {
  const wrapper = editorWrapper.value
  if (!tagIsVisible.value || !tagCaretRect || !wrapper) {
    return
  }
  const dropdown = wrapper.querySelector(`#${tagListboxId}`)
  const height = dropdown ? dropdown.offsetHeight : 0
  const wrapperRect = wrapper.getBoundingClientRect()
  const bounds = getVisibleBounds(wrapper)
  const spaceBelow = bounds.bottom - tagCaretRect.bottom - TAG_DROPDOWN_GAP
  const spaceAbove = tagCaretRect.top - TAG_DROPDOWN_GAP - bounds.top
  const top = height > spaceBelow && spaceAbove > spaceBelow
    ? tagCaretRect.top - TAG_DROPDOWN_GAP - height
    : tagCaretRect.bottom + TAG_DROPDOWN_GAP
  const remInPx = parseFloat(window.getComputedStyle(document.documentElement).fontSize)
  const maxLeft = wrapperRect.width - TAG_DROPDOWN_MIN_WIDTH_REM * remInPx
  tagPosition.value = {
    top: top - wrapperRect.top,
    left: Math.max(0, Math.min(tagCaretRect.left - wrapperRect.left, maxLeft))
  }
}

// Keeps the highlighted row on screen. At large text sizes the list can run past the bottom of the modal or window,
// and arrowing down would otherwise move the highlight out of sight.
const scrollTagHighlightIntoView = () => {
  if (hasTagOptions()) {
    document.getElementById(optionId(tagListboxId, tagHighlightedIndex.value))?.scrollIntoView({block: 'nearest'})
  }
}

const showTagMessage = message => {
  tagIsLoading.value = false
  tagMessage.value = message
  tagUsers.value = []
  alertScreenReader(message)
}

// Points the CKEditor text box at the dropdown while it's open, and clears that when it closes. This goes through the
// editing view: CKEditor's renderer strips any DOM attribute on the editable that the view doesn't know about, which
// happens on every re-render, including focus changes. There's no aria-expanded, which role="textbox" doesn't allow.
const syncTagAria = () => {
  const view = toRaw(editor.value).editing.view
  view.change(writer => {
    const root = view.document.getRoot()
    if (tagIsVisible.value) {
      writer.setAttribute('aria-controls', tagListboxId, root)
      writer.setAttribute('aria-autocomplete', 'list', root)
    } else {
      writer.removeAttribute('aria-controls', root)
      writer.removeAttribute('aria-autocomplete', root)
    }
    if (hasTagOptions()) {
      writer.setAttribute('aria-activedescendant', optionId(tagListboxId, tagHighlightedIndex.value), root)
    } else {
      writer.removeAttribute('aria-activedescendant', root)
    }
  })
}

// Both run after Vue has rendered the change, so aria-activedescendant never names an option that isn't in the DOM yet,
// and placement measures the dropdown's new height. Watchers stop on unmount, so neither touches a destroyed editor.
watch([tagHighlightedIndex, tagIsLoading, tagIsVisible, tagMessage, tagUsers], syncTagAria, {flush: 'post'})
// Runs before the render these changes cause, to mark it for onUpdated.
watch([tagHighlightedIndex, tagIsLoading, tagIsVisible, tagMessage, tagPosition, tagUsers], () => {
  isTagRender = true
}, {flush: 'pre'})
watch([tagIsLoading, tagIsVisible, tagMessage, tagUsers], placeTagDropdown, {flush: 'post'})
// Waits one more tick so the scroll happens after the re-render that placement's new position causes.
watch([tagHighlightedIndex, tagUsers], () => nextTick(scrollTagHighlightIntoView), {flush: 'post'})
// The Esc listener is attached only while the dropdown is open, so Esc behaves normally the rest of the time.
watch(tagIsVisible, isVisible => {
  if (isVisible) {
    window.addEventListener('keydown', onTagEscapeKeyDown, {capture: true})
  } else {
    window.removeEventListener('keydown', onTagEscapeKeyDown, {capture: true})
  }
})
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
/* The hint after a bare "@" (see user-tags.ts). Generated content, so it is never saved or selectable. It is positioned
  absolutely so it takes no room in the line: the browser puts the caret after the "@" span, and an inline hint would push
  the caret to the end of the word "name". The second content declaration gives it an empty text alternative, so screen
  readers don't read "name" as part of the note; browsers without that syntax keep the first. #595959 on white is 7:1. */
.ck-content .user-tag-hint {
  position: relative;
}
.ck-content .user-tag-hint::after {
  color: #595959;
  content: 'name';
  content: 'name' / '';
  font-style: italic;
  left: 100%;
  /* The page's line-height (1.5) would make this box taller than the "@" and push the hint down. "normal" gives it the
     same height as the "@", so the two share a baseline. */
  line-height: normal;
  pointer-events: none;
  position: absolute;
  top: 0;
  white-space: nowrap;
}
/* A tag in the editor is blue text on a small pale-blue chip, which marks where the tag begins and ends. This replaces
   CKEditor's default pink mention style. The colors are fixed rather than taken from the theme, because the theme's blues
   are muted and read as gray here. #0b61a4 on the chip's #e5f1fb is about 5.6:1, above the 4.5:1 AA minimum. */
.ck.ck-content .mention {
  background-color: #e5f1fb;
  border: 1px solid #a9cdea;
  border-radius: 0.2rem;
  box-decoration-break: clone;
  color: #0b61a4;
  font-weight: normal;
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
  height: 11.25rem;
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
