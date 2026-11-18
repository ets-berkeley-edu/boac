import {
  type Batch,
  type Editor,
  type EventInfo,
  type ModelDocumentChangeEvent,
  type ModelPosition,
  type ModelRange,
  type ObservableChangeEvent,
  TextWatcher,
  type TextWatcherMatchedDataEvent,
  type TextWatcherMatchedTypingSelectionEvent,
  type TextWatcherUnmatchedTypingEvent,
  type ViewDocumentKeyDownEvent,
  type ViewDocumentKeyEventData,
  keyCodes
} from 'ckeditor5'
import type {TaggableUser} from '@/lib/types'
import {UNKNOWN_USER_NAME} from '@/lib/user-tags'

/*
* Glue between CKEditor and BOA's own UserTagDropdown for "@" user tags. It spots "@text" before the caret,
* steals the dropdown's keys from the editor, and inserts the chosen user through CKEditor's 'mention' command.
*
* CKEditor's own MentionUI dropdown is never shown: it's a private view with no listbox/option ARIA, so screen reader
* users can't tell what's offered. RichTextEditor loads the whole Mention plugin with no feeds, which keeps MentionUI
* inert, and renders an accessible dropdown that this module feeds. The 'mention' command comes from that Mention plugin.
*/

export interface UserTagMatch {
  typedText: string,
  range: ModelRange,
  caretRect: DOMRect
}

export interface UserTagCallbacks {
  allowBareMarker: () => boolean
  hasOptions: () => boolean
  isVisible: () => boolean
  onMatch: (match: UserTagMatch) => void
  onClose: () => void
  onMove: (delta: 1 | -1) => void
  onCommit: () => void
}

// What opens the dropdown while typing (not the stored-tag rule, which is USER_TAG_PATTERN in src/lib/user-tags.ts):
// "@" at the start of a line, or after whitespace or opening punctuation, then up to 40 characters. Excluding "@"
// from the typed text means a second "@" later in the line always wins, and "foo@bar" (an email) never matches.
// None of the characters allowed before "@" is a word character, "@" or "/", so a picked tag never starts out glued.
const USER_TAG_TRIGGER_PATTERN = /(?:^|[\s(["'])@([^@\n]{0,40})$/u

// A bare "@" the author has just typed, with nothing after it yet.
const BARE_MARKER_PATTERN = /(?:^|[\s(["'])@$/u

// The model marker that tags the bare "@". mention-uid.ts turns it into the view class RichTextEditor styles.
export const USER_TAG_HINT_MARKER = 'user-tag-hint'

type UserTagTestResult = {typedText: string}

export function attachUserTagAutocomplete(editor: Editor, callbacks: UserTagCallbacks): () => void {
  const model = editor.model
  const viewDocument = editor.editing.view.document
  // The Mention plugin registers this command. Fail loudly here, rather than with an obscure error on the first
  // keystroke, if a caller turns tagging on without loading that plugin.
  const mentionCommand = editor.commands.get('mention')
  if (!mentionCommand) {
    throw new Error('User tag autocomplete needs the Mention plugin, which registers the \'mention\' command. Add Mention (with mention: {feeds: []}) to the editor\'s plugins.')
  }

  // TextWatcher hands us the text of the current line up to the caret. Returning an object both signals a match and
  // passes the typed text along to the 'matched:*' events.
  const testCallback = (text: string): UserTagTestResult | false => {
    const match = text.match(USER_TAG_TRIGGER_PATTERN)
    if (!match) {
      return false
    }
    const typedText = match[1]
    if (!typedText && !callbacks.allowBareMarker()) {
      return false
    }
    // The text ends at the caret, so the "@" sits (1 + typedText.length) offsets before it. If that "@" is part of
    // an existing tag, don't reopen the dropdown: otherwise "@Name " right after a pick would match all over again.
    const markerPosition = model.document.selection.focus!.getShiftedBy(-(1 + typedText.length))
    return isInExistingMention(markerPosition) ? false : {typedText}
  }
  const watcher = new TextWatcher(model, testCallback)
  // The 'mention' command is disabled in a read-only editor, or where the schema doesn't allow tags. Tying the watcher
  // to it means a disabled editor never opens the dropdown, even when the user clicks into existing "@text".
  watcher.bind('isEnabled').to(mentionCommand)

  // TextWatcher fires 'matched:data' from the model's 'change:data' event at normal priority. The editing view isn't
  // updated until a later, low-priority listener converts the change and rendering resumes when the change block ends.
  // Mapping the new range to the view right away would throw 'mapping-model-offset-not-found' and break typing.
  // So we measure in a microtask, which runs after the whole synchronous change block has converted and rendered.
  // The counter lets a newer match, a close, or detach() cancel a report that is still waiting.
  let matchGeneration = 0
  const cancelPendingMatch = () => matchGeneration++

  // Typing ('matched:data') and moving the caret into "@text" ('matched:selection') are handled the same way.
  const onMatched = (evt: EventInfo, data: {range: ModelRange} & UserTagTestResult) => {
    const {typedText} = data
    // TextWatcher's range covers the whole line before the caret. Narrow it to the "@" through the caret, which is
    // the text the 'mention' command will replace.
    const range = model.createRange(data.range.end.getShiftedBy(-(1 + typedText.length)), data.range.end)
    const generation = ++matchGeneration
    queueMicrotask(() => {
      if (generation !== matchGeneration) {
        return
      }
      try {
        const viewRange = editor.editing.mapper.toViewRange(range)
        const caretRect = editor.editing.view.domConverter.viewRangeToDom(viewRange).getBoundingClientRect()
        callbacks.onMatch({typedText, range, caretRect})
      } catch {
        // The document changed under us before we could measure (or the match couldn't be shown). Close rather than
        // leave the dropdown pointing at a range that may no longer be there; the next keystroke tries again.
        callbacks.onClose()
      }
    })
  }
  watcher.on<TextWatcherMatchedDataEvent<UserTagTestResult>>('matched:data', onMatched)
  watcher.on<TextWatcherMatchedTypingSelectionEvent<UserTagTestResult>>('matched:selection', onMatched)
  watcher.on<TextWatcherUnmatchedTypingEvent>('unmatched', () => {
    cancelPendingMatch()
    callbacks.onClose()
  })

  // If the editor becomes disabled (e.g. read-only while a note saves) with the dropdown open, close it.
  const onCommandEnabledChange = (evt: EventInfo, name: string, isEnabled: boolean) => {
    if (!isEnabled) {
      cancelPendingMatch()
      callbacks.onClose()
    }
  }
  mentionCommand.on<ObservableChangeEvent<boolean>>('change:isEnabled', onCommandEnabledChange)

  // TextWatcher skips undo batches, so after undo or redo the dropdown would stay open over text that has changed. Close
  // it instead. CKEditor marks both undo and redo batches with isUndo.
  const onDataChange = (evt: EventInfo, batch: Batch) => {
    if (batch.isUndo) {
      cancelPendingMatch()
      callbacks.onClose()
    }
  }
  model.document.on<ModelDocumentChangeEvent>('change:data', onDataChange)

  // Close when focus leaves the text box itself, including a move to the editor's toolbar, where our key handling no
  // longer applies. The dropdown cancels mousedown, so clicking in it doesn't count as leaving.
  const onFocusChange = (evt: EventInfo, name: string, isFocused: boolean) => {
    if (!isFocused) {
      cancelPendingMatch()
      callbacks.onClose()
    }
  }
  viewDocument.on<ObservableChangeEvent<boolean>>('change:isFocused', onFocusChange)

  // The gray "name" hint. While the caret sits right after a bare "@" (and no dropdown is wanted, as on a batch note, which
  // explains itself instead), a marker over that "@" lets the editor's CSS draw the hint after it. The marker is not part
  // of the document, so it is never saved, never undone, and never read by the glue above.
  const getBareMarkerRange = (): ModelRange | null => {
    const selection = model.document.selection
    if (!mentionCommand.isEnabled || !viewDocument.isFocused || !selection.isCollapsed || callbacks.allowBareMarker()) {
      return null
    }
    const caret = selection.focus!
    // The hint is drawn over the space after the "@", so it is shown only when no text follows the caret to be covered.
    if (!caret.isAtEnd) {
      return null
    }
    // Only the text right before the caret matters; look back a couple of characters, not the whole line.
    const start = model.createPositionAt(caret.parent, Math.max(0, caret.offset - 2))
    let text = ''
    for (const item of model.createRange(start, caret).getItems()) {
      text += item.is('$textProxy') ? item.data : '\0'
    }
    // Two characters are enough for the pattern, but "@" at offset 1 means the line starts with it.
    const atLineStart = caret.offset === 1
    if (!(atLineStart ? text === '@' : BARE_MARKER_PATTERN.test(text))) {
      return null
    }
    const markerPosition = caret.getShiftedBy(-1)
    return isInExistingMention(markerPosition) ? null : model.createRange(markerPosition, caret)
  }

  // Runs in a microtask, after the change that triggered it, because the model can't be changed from inside its own
  // change event. The counter lets a newer update, or detach(), cancel one that is still waiting.
  let hintGeneration = 0
  const updateHint = () => {
    const generation = ++hintGeneration
    queueMicrotask(() => {
      if (generation !== hintGeneration) {
        return
      }
      const range = getBareMarkerRange()
      const existing = model.markers.get(USER_TAG_HINT_MARKER)
      if (existing && range && existing.getRange().isEqual(range)) {
        return
      }
      model.change(writer => {
        if (existing) {
          writer.removeMarker(USER_TAG_HINT_MARKER)
        }
        if (range) {
          writer.addMarker(USER_TAG_HINT_MARKER, {range, usingOperation: false, affectsData: false})
        }
      })
    })
  }
  model.document.on('change:data', updateHint)
  model.document.selection.on('change:range', updateHint)
  viewDocument.on('change:isFocused', updateHint)
  mentionCommand.on('change:isEnabled', updateHint)

  // 'highest' priority so we act before CKEditor's own Enter, Tab, and arrow handling. Stopping the native event
  // keeps Esc from also reaching the note modal's @keydown.esc handler, which would close the whole modal. (A modal that
  // listens in the capture phase hears Esc before this runs; RichTextEditor's window capture listener covers that.)
  const onKeyDown = (evt: EventInfo, data: ViewDocumentKeyEventData) => {
    // Only plain keys drive the dropdown. Shift+Tab must keep moving focus backward out of the editor, a modified
    // Enter keeps its usual editor meaning (e.g. Shift+Enter for a line break), and modified arrows keep selecting text
    // or jumping the caret.
    const hasModifier = data.shiftKey || data.ctrlKey || data.metaKey || data.altKey
    let handled = false
    if (callbacks.hasOptions()) {
      handled = true
      switch (data.keyCode) {
      case keyCodes.arrowup:
      case keyCodes.arrowdown:
        if (hasModifier) {
          handled = false
        } else {
          callbacks.onMove(data.keyCode === keyCodes.arrowup ? -1 : 1)
        }
        break
      case keyCodes.enter:
      case keyCodes.tab:
        if (hasModifier) {
          handled = false
        } else {
          callbacks.onCommit()
        }
        break
      case keyCodes.esc:
        callbacks.onClose()
        break
      default:
        handled = false
      }
    } else if (callbacks.isVisible() && data.keyCode === keyCodes.esc) {
      // Only a message row is showing (e.g. "Searching…"), so there's nothing to move to or pick. Esc still dismisses it.
      handled = true
      callbacks.onClose()
    }
    if (handled) {
      evt.stop()
      data.preventDefault()
      data.domEvent.stopPropagation()
    }
  }
  viewDocument.on<ViewDocumentKeyDownEvent>('keydown', onKeyDown, {priority: 'highest'})

  return () => {
    cancelPendingMatch()
    hintGeneration++
    model.document.off('change:data', updateHint)
    model.document.selection.off('change:range', updateHint)
    viewDocument.off('change:isFocused', updateHint)
    mentionCommand.off('change:isEnabled', updateHint)
    if (model.markers.has(USER_TAG_HINT_MARKER)) {
      model.change(writer => writer.removeMarker(USER_TAG_HINT_MARKER))
    }
    // TextWatcher has no destroy(). unbind() drops the link to the 'mention' command. Its own listeners, and ours
    // registered with watcher.on(), all go through listenTo(), so stopListening() tears down the rest.
    watcher.unbind('isEnabled')
    watcher.stopListening()
    mentionCommand.off('change:isEnabled', onCommandEnabledChange)
    model.document.off('change:data', onDataChange)
    viewDocument.off('change:isFocused', onFocusChange)
    viewDocument.off('keydown', onKeyDown)
  }
}

export function insertUserTag(editor: Editor, range: ModelRange, user: TaggableUser): void {
  // The BOA UID goes in 'userUid', never 'uid'. CKEditor already puts its own per-instance id in the mention's 'uid'.
  // Overwriting it would make two adjacent tags of the same person look like one mention and merge into one.
  // A person with an empty name gets the same label as any unknown name, so the tag never reads as a bare "@".
  const name = user.name || UNKNOWN_USER_NAME
  editor.execute('mention', {
    marker: '@',
    mention: {id: '@' + name, userUid: user.uid},
    text: '@' + name,
    range
  })
}

// Checks that the "@text" a dropdown was opened for is still exactly where it was. Undo doesn't make TextWatcher look at
// the text again, so the dropdown can outlive what it was opened for, and inserting over a stale range would replace the
// wrong text. A stale position can point outside the tree, which makes CKEditor throw; that counts as not current.
export function isUserTagRangeCurrent(range: ModelRange, typedText: string): boolean {
  try {
    let text = ''
    for (const item of range.getItems()) {
      if (!item.is('$textProxy')) {
        return false
      }
      text += item.data
    }
    return text === '@' + typedText
  } catch {
    return false
  }
}

// The same check MentionUI makes. A position in the middle of a text node reports it as textNode; a position at a node
// boundary reports the node that starts there as nodeAfter.
function isInExistingMention(position: ModelPosition): boolean {
  const node = position.textNode || position.nodeAfter
  return !!node && node.is('$text') && node.hasAttribute('mention')
}
