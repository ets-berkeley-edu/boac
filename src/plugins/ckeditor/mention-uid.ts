import {
  type Batch,
  type DeleteEventData,
  type EventInfo,
  Mention,
  type MentionAttribute,
  type Model,
  type ModelDocumentChangeEvent,
  type ModelDocumentFragment,
  type ModelElement,
  type ModelNode,
  type ModelRange,
  type ModelWriter,
  Plugin,
  type UpcastElementEvent,
  type ViewDocumentDeleteEvent,
  type ViewElement,
  ViewUpcastWriter
} from 'ckeditor5'
import {USER_TAG_HINT_MARKER} from '@/plugins/ckeditor/user-tags'
import {alertScreenReader} from '@/lib/utils'

/*
* Carries a BOA user tag's UID between the editor's model and its HTML. In the model, a tag is a CKEditor mention whose
* BOA UID sits in 'userUid'. In HTML it is <span class="mention" data-mention="@<name>" data-uid="<uid>">@<name></span>,
* which the UserTagData processor turns into the stored "@<UID>" text. This is CKEditor's documented "customizing the
* output" pattern for mentions, plus BOA rules: a tag is deleted whole, a tag shows the trusted name for its UID, a tag
* glued to a neighboring word turns into plain text, and screen readers hear when an edit turns a tag into plain text.
*/

// The mention attribute as BOA uses it. 'uid' is CKEditor's own per-instance id; 'userUid' is the BOA UID.
type UserTagMention = MentionAttribute & {userUid?: string}

type NameFor = (uid: string) => string | null | undefined

export default class MentionUid extends Plugin {
  static get requires() {
    return [Mention]
  }

  static get pluginName() {
    return 'MentionUid'
  }

  init(): void {
    this.addUpcast()
    this.addDowncast()
    // Registered after MentionEditing's own post-fixers (Mention requires it, so it initializes first). Those strip the
    // mention from any partial or broken tag before ours looks at what's left.
    this.editor.model.document.registerPostFixer(writer => this.showTrustedNames(writer))
    this.editor.model.document.registerPostFixer(writer => this.unglueTags(writer))
    this.addAtomicDelete()
    this.announceRemovedTags()
    // user-tags.ts marks a bare "@" while the author is about to type a name. Editing view only, so the mark never reaches
    // the saved body; RichTextEditor's CSS draws the gray "name" hint after it.
    this.editor.conversion.for('editingDowncast').markerToHighlight({model: USER_TAG_HINT_MARKER, view: {classes: 'user-tag-hint'}})
  }

  // The name lookup RichTextEditor puts in config. Without it, every UID counts as unknown and pasted text is kept.
  private nameFor(uid: string): string | null | undefined {
    const nameFor = this.editor.config.get('userTags.nameFor')
    return typeof nameFor === 'function' ? (nameFor as NameFor)(uid) : undefined
  }

  private addUpcast(): void {
    const mentionPlugin = this.editor.plugins.get(Mention)
    // 'high' runs before MentionEditing's own span converter, which then finds the span already consumed. A span that
    // isn't a BOA tag (no all-digits data-uid) doesn't match here; the converter below turns it into plain text. Only an
    // all-digits data-uid counts, the same rule the save path (fromEditorHtml) uses to turn a span into "@<UID>".
    this.editor.conversion.for('upcast').elementToAttribute({
      view: {
        name: 'span',
        classes: 'mention',
        attributes: {'data-mention': true, 'data-uid': /^\d+$/}
      },
      model: {
        key: 'mention',
        value: (viewItem: ViewElement) => {
          const userUid = viewItem.getAttribute('data-uid') as string
          const name = this.nameFor(userUid)
          // A known name wins over the span's own data-mention, so a pasted or crafted span can't label one person's UID
          // with another's name. The span's text can't be changed from here (an attribute converter only marks the text
          // its children produce), so the showTrustedNames post-fixer rewrites that text right after.
          const data = typeof name === 'string' ? {userUid, id: '@' + name} : {userUid}
          // Mention#toMentionAttribute takes a view element at runtime; its 48.5.3 typings mislabel it as ModelElement.
          return mentionPlugin.toMentionAttribute(viewItem as unknown as ModelElement, data)
        }
      },
      converterPriority: 'high'
    })
    // A span.mention that isn't a BOA tag (no data-mention, or no all-digits data-uid) can only come from pasted content.
    // Consuming its "mention" class stops MentionEditing's converter from making it a mention, so it never looks like a
    // tag. CKEditor's fallback element converter then keeps its children as plain text.
    this.editor.conversion.for('upcast').add(dispatcher => {
      dispatcher.on<UpcastElementEvent>('element:span', (evt, data, conversionApi) => {
        const span = data.viewItem
        if (span.hasClass('mention') && !isUserTagSpan(span)) {
          conversionApi.consumable.consume(span, {classes: 'mention'})
        }
      }, {priority: 'high'})
    })
  }

  private addDowncast(): void {
    // One converter for editing, data, and the clipboard. CKEditor's default leaves out its own instance id when
    // options.isClipboardPipeline is set; ours always writes data-uid, so a copied tag pastes back as a tag.
    this.editor.conversion.for('downcast').attributeToElement({
      model: 'mention',
      view: (value: UserTagMention | null, {writer}) => {
        // A mention without a BOA UID isn't ours. Returning nothing leaves it to MentionEditing's default converter.
        if (!value?.userUid) {
          return undefined
        }
        // Keying the element on CKEditor's per-instance uid keeps two adjacent tags of the same person as two spans.
        return writer.createAttributeElement(
          'span',
          {class: 'mention', 'data-mention': value.id, 'data-uid': value.userUid},
          {priority: 20, id: value.uid}
        )
      },
      converterPriority: 'high'
    })
  }

  // Makes every newly inserted tag read "@<trusted name>" whenever its UID's name is known. On load the text already
  // matches (toEditorHtml writes the trusted name), so this only acts on pasted or dropped tags whose text disagrees.
  // It fixes one tag per call and returns true, and CKEditor keeps calling post-fixers until none report a change.
  private showTrustedNames(writer: ModelWriter): boolean {
    const model = this.editor.model
    for (const change of model.document.differ.getChanges()) {
      if (change.type !== 'insert' || change.position.root === model.document.graveyard) {
        continue
      }
      const inserted = model.createRange(change.position, change.position.getShiftedBy(change.length))
      for (const item of inserted.getItems()) {
        if (!item.is('$textProxy')) {
          continue
        }
        const mention = getUserTagMention(item.textNode)
        const name = mention ? this.nameFor(mention.userUid) : undefined
        if (!mention || typeof name !== 'string') {
          continue
        }
        const text = '@' + name
        const range = getMentionRange(model, item.textNode)
        if (getText(range) === text && mention.id === text) {
          continue
        }
        // Insert the corrected tag in front of the old one, then remove the old one. A caret after the tag moves along
        // with it this way. The new tag keeps the old one's other formatting (bold, italic).
        const attributes = new Map(range.start.nodeAfter!.getAttributes())
        attributes.set('mention', this.createMention(name, mention.userUid))
        writer.insertText(text, attributes, range.start)
        writer.remove(model.createRange(range.start.getShiftedBy(text.length), range.end.getShiftedBy(text.length)))
        return true
      }
    }
    return false
  }

  // A tag flush against a neighboring character that would glue it in the saved body (see isGluedTag) would save as
  // its name text, not "@<UID>" (fromEditorHtml's safety net). Stripping the tag here shows that to the author right
  // away, as plain text, instead of a chip that silently isn't one. It removes one tag per call and returns true; each
  // call leaves one fewer mention, so the post-fixer loop always ends. A pick never trips it: the typing trigger allows
  // only whitespace, an opening bracket or a quote before "@", and the mention command adds a space after the tag.
  private unglueTags(writer: ModelWriter): boolean {
    const model = this.editor.model
    for (const parent of getChangedParents(model)) {
      for (const child of parent.getChildren()) {
        if (!getUserTagMention(child)) {
          continue
        }
        const range = getMentionRange(model, child)
        if (isGluedTag(range)) {
          writer.removeAttribute('mention', range)
          return true
        }
      }
    }
    return false
  }

  // Announces "Removed tag <name>" when an edit turns a tag into plain text: a partial edit (MentionEditing's post-fixer)
  // or a glued tag (unglueTags). Those keep the text and drop its mention attribute, which the differ reports as an
  // attribute change. Loading content and the trusted-name rewrite insert fresh text, and atomic delete removes the text
  // (it announces on its own), so none of them shows up here. Undo and redo stay quiet, as they do for the dropdown.
  private announceRemovedTags(): void {
    const modelDocument = this.editor.model.document
    this.listenTo<ModelDocumentChangeEvent>(modelDocument, 'change:data', (evt: EventInfo, batch: Batch) => {
      if (batch.isUndo) {
        return
      }
      // One tag's text can show up as several attribute changes (e.g. the parts on either side of a typed character),
      // so names are keyed by CKEditor's per-instance uid and each tag is announced once.
      const removed = new Map<string, string>()
      for (const change of modelDocument.differ.getChanges()) {
        if (change.type !== 'attribute' || change.attributeKey !== 'mention' || change.attributeNewValue !== null) {
          continue
        }
        const mention = change.attributeOldValue as UserTagMention | null
        if (mention?.userUid) {
          removed.set(mention.uid, mention.id.replace(/^@/, ''))
        }
      }
      if (removed.size) {
        // alertScreenReader keeps only its latest message, so several tags broken by one edit share one announcement.
        alertScreenReader(Array.from(removed.values(), name => `Removed tag ${name}`).join('. '))
      }
    })
  }

  // Builds a fresh mention for "@<name>" through Mention's public toMentionAttribute. It reads the tag's text from a view
  // element, so we hand it a throwaway span. That keeps CKEditor's broken-tag check (text vs. recorded text) satisfied.
  private createMention(name: string, userUid: string): UserTagMention | undefined {
    const viewWriter = new ViewUpcastWriter(this.editor.data.viewDocument)
    const text = '@' + name
    const span = viewWriter.createElement('span', {'data-mention': text}, viewWriter.createText(text))
    return this.editor.plugins.get(Mention).toMentionAttribute(span as unknown as ModelElement, {userUid})
  }

  // CKEditor's default Backspace removes one character of a tag, which turns the rest into plain "@Jane Adviso" text.
  // A plain Backspace right after a tag, or a plain Delete right before one, removes the whole tag instead.
  private addAtomicDelete(): void {
    const editor = this.editor
    const model = editor.model
    const viewDocument = editor.editing.view.document
    const onDelete = (evt: EventInfo, data: DeleteEventData) => {
      if (viewDocument.isComposing) {
        return
      }
      // A plain Backspace arrives as a backward 'codePoint' delete and a plain Delete as a forward 'character' one.
      // Word and line deletes (Alt/Ctrl/Cmd+Backspace) and deleting a selection use other units, so they keep the default.
      const isBackward = data.direction === 'backward'
      if (data.unit !== (isBackward ? 'codePoint' : 'character')) {
        return
      }
      const selection = model.document.selection
      const position = selection.getFirstPosition()
      // A caret inside a tag's text (textNode is set) isn't next to it, so that partial edit keeps the default too.
      if (!selection.isCollapsed || !position || position.textNode) {
        return
      }
      const node = isBackward ? position.nodeBefore : position.nodeAfter
      const mention = getUserTagMention(node)
      const commandName = isBackward ? 'delete' : 'deleteForward'
      if (!node || !mention || !editor.commands.get(commandName)?.isEnabled) {
        return
      }
      const range = getMentionRange(model, node)
      if (!model.canEditAt(range)) {
        return
      }
      // Going through the delete command keeps the read-only check and groups the change with nearby typing for undo.
      editor.execute(commandName, {selection: model.createSelection(range), sequence: data.sequence})
      editor.editing.view.scrollToTheSelection()
      data.preventDefault()
      evt.stop()
      alertScreenReader(`Removed tag ${mention.id.replace(/^@/, '')}`)
    }
    // 'high' runs before the Delete plugin's own handler ('low'), which would otherwise delete a single character.
    this.listenTo<ViewDocumentDeleteEvent>(viewDocument, 'delete', onDelete, {priority: 'high'})
  }
}

// The node's mention when it is a BOA tag (one with a userUid), or null. Any other mention isn't treated as a tag, so
// atomic delete, the trusted name, and the "Removed tag" announcement leave it alone.
function getUserTagMention(node: ModelNode | null): (UserTagMention & {userUid: string}) | null {
  const mention = node?.is('$text') ? node.getAttribute('mention') as UserTagMention | undefined : undefined
  return mention?.userUid ? mention as UserTagMention & {userUid: string} : null
}

// Whether a view span is a BOA tag: the same rule the BOA upcast matches on and fromEditorHtml saves by.
function isUserTagSpan(span: ViewElement): boolean {
  const uid = span.getAttribute('data-uid')
  return span.hasAttribute('data-mention') && typeof uid === 'string' && /^\d+$/.test(uid)
}

// The elements whose children this change block touched (inserted, removed, or reformatted), skipping removed content.
// The glue check only needs to look at tags in these, since a tag can only become glued when something beside it changes.
function getChangedParents(model: Model): Set<ModelElement | ModelDocumentFragment> {
  const parents = new Set<ModelElement | ModelDocumentFragment>()
  const add = (parent: ModelElement | ModelDocumentFragment) => {
    if (parent.root !== model.document.graveyard && parent.root.is('rootElement')) {
      parents.add(parent)
    }
  }
  for (const change of model.document.differ.getChanges()) {
    const range = change.type === 'attribute'
      ? change.range
      : model.createRange(change.position, change.type === 'insert' ? change.position.getShiftedBy(change.length) : change.position)
    add(range.start.parent)
    add(range.end.parent)
    // An inserted or reformatted block (a pasted paragraph, a list item) holds its text one level down.
    for (const item of range.getItems()) {
      if (item.is('$textProxy')) {
        add(item.parent as ModelElement)
      }
    }
  }
  return parents
}

// Whether a tag sits flush against a character that would glue it in the saved body, by the same rule as
// fromEditorHtml: the text before it ends in a word character, "@" or "/", or the text after it starts with a word
// character. A neighbor only counts when it has the tag's own formatting (bold, italic, link). Then both sit in the same
// HTML element, side by side; with different formatting an element boundary separates them, and the backend reads that
// "<" or ">" as a break. A neighboring tag counts as the "@<UID>" it saves as.
function isGluedTag(range: ModelRange): boolean {
  const first = range.start.nodeAfter!
  const last = range.end.nodeBefore!
  return /[\w@/]$/.test(savedNeighborText(first, first.previousSibling)) || /^\w/.test(savedNeighborText(last, last.nextSibling))
}

function savedNeighborText(tagNode: ModelNode, neighbor: ModelNode | null): string {
  if (!neighbor?.is('$text') || !hasSameFormatting(tagNode, neighbor)) {
    return ''
  }
  const mention = getUserTagMention(neighbor)
  return mention ? '@' + mention.userUid : neighbor.data
}

// Compares every attribute except 'mention'.
function hasSameFormatting(a: ModelNode, b: ModelNode): boolean {
  const formatting = (node: ModelNode) => Array.from(node.getAttributes()).filter(([key]) => key !== 'mention')
  const aFormatting = formatting(a)
  const bFormatting = formatting(b)
  return aFormatting.length === bFormatting.length && aFormatting.every(([key, value]) => b.getAttribute(key) === value)
}

// The whole tag around a node: its contiguous siblings with the same mention instance (CKEditor's per-instance uid). A
// tag can span several text nodes if part of it is formatted differently. Two adjacent tags of the same person have
// different uids, so this never joins them.
function getMentionRange(model: Model, node: ModelNode): ModelRange {
  const uid = getUserTagMention(node)?.uid
  let first = node
  let last = node
  for (let sibling = first.previousSibling; sibling && getUserTagMention(sibling)?.uid === uid; sibling = sibling.previousSibling) {
    first = sibling
  }
  for (let sibling = last.nextSibling; sibling && getUserTagMention(sibling)?.uid === uid; sibling = sibling.nextSibling) {
    last = sibling
  }
  return model.createRange(model.createPositionBefore(first), model.createPositionAfter(last))
}

function getText(range: ModelRange): string {
  let text = ''
  for (const item of range.getItems()) {
    text += item.is('$textProxy') ? item.data : ''
  }
  return text
}
