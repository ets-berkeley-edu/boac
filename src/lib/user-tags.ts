// Shared helpers for user tags (the @ autocomplete in note and comment editors).
// Note and comment bodies store a tag as plain `@<UID>`. The editor shows it as a mention span with the person's name.
// toEditorHtml and fromEditorHtml convert between the two; the editor's data processor calls them on every load and save.

// Builds the DOM id of one option in the tag dropdown. The dropdown renders it and the editor plugin
// points aria-activedescendant at it, so both must build the id the same way.
export function optionId(listboxId: string, index: number): string {
  return `${listboxId}-option-${index}`
}

// Each editor's tag dropdown needs a listbox id no other editor on the page shares, or aria-controls and
// aria-activedescendant would point at the wrong list. A counter, not a timestamp: two editors can mount in the same
// millisecond.
let listboxCount = 0
export function nextUserTagListboxId(): string {
  listboxCount++
  return `user-tag-listbox-${listboxCount}`
}

// What a tag looks like in a stored body: `@` plus digits, not glued to a word, another `@` or a `/` (so emails and URL
// paths don't match). It's the one definition of the rule, and it is meant to be run against a single text node's text,
// never against raw HTML. That means the lookbehind can't see across an element boundary, so `a<b>@1</b>` still matches.
// The `g` flag lets matchAll() walk every tag in a node. matchAll copies this shared object's lastIndex into its own
// clone and starts there, so callers must never run .test() or .exec() on it (which move lastIndex); clone it first.
export const USER_TAG_PATTERN = /(?<![\w@/])@(\d+)\b/g

// Label for a tag whose person the backend couldn't find, or whose name is empty. The tag still saves as @<UID>.
export const UNKNOWN_USER_NAME = 'Unknown user'

// Builds the mention span the editor's mention plugin reads. The DOM API (not string concatenation) sets the name, so a
// name containing quotes or angle brackets can't break out of the attribute or the element.
function buildMentionSpan(doc: Document, uid: string, name: string): HTMLSpanElement {
  const span = doc.createElement('span')
  span.setAttribute('class', 'mention')
  span.setAttribute('data-mention', `@${name}`)
  span.setAttribute('data-uid', uid)
  span.textContent = `@${name}`
  return span
}

// Converts a stored body (tags as @<UID>) to the HTML the editor loads (tags as mention spans). `nameFor` says what is
// known about a UID: a string is the person's name, null means the backend found no name (shown as "Unknown user"), and
// undefined means the UID wasn't a tag at all, so its text stays as typed. Link text is converted like any other text,
// so a tag inside a link shows as a name; a link's URL is an attribute, which the text walk never visits.
export function toEditorHtml(body: string, nameFor: (uid: string) => string | null | undefined): string {
  // Fast path: most bodies have no @, so they skip parsing entirely.
  if (!body || !body.includes('@')) {
    return body
  }
  const doc = new DOMParser().parseFromString(body, 'text/html')
  // Collect the text nodes first. Replacing nodes while the TreeWalker is still walking would disturb it.
  const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT)
  const textNodes: Text[] = []
  for (let node = walker.nextNode(); node; node = walker.nextNode()) {
    textNodes.push(node as Text)
  }
  let changed = false
  for (const textNode of textNodes) {
    const text = textNode.data
    const replacements: Node[] = []
    let lastIndex = 0
    for (const match of text.matchAll(USER_TAG_PATTERN)) {
      const uid = match[1]
      const name = nameFor(uid)
      if (name === undefined) {
        // Not a known tag: leave this match in the surrounding text.
        continue
      }
      if (match.index > lastIndex) {
        replacements.push(doc.createTextNode(text.slice(lastIndex, match.index)))
      }
      replacements.push(buildMentionSpan(doc, uid, name || UNKNOWN_USER_NAME))
      lastIndex = match.index + match[0].length
    }
    if (replacements.length) {
      if (lastIndex < text.length) {
        replacements.push(doc.createTextNode(text.slice(lastIndex)))
      }
      textNode.replaceWith(...replacements)
      changed = true
    }
  }
  // When nothing became a mention, return the body untouched so parsing can't reformat HTML we never meant to change.
  return changed ? doc.body.innerHTML : body
}

// Converts the editor's HTML (tags as mention spans) back to the stored form (tags as @<UID>). A span without a
// data-uid, or one whose data-uid isn't all digits, can't come from our picker, only from pasted content, so it's
// unwrapped to its plain text rather than saved as a tag with no person behind it.
export function fromEditorHtml(html: string): string {
  // Fast path: no "mention" means no tag spans, so skip parsing.
  if (!html || !html.includes('mention')) {
    return html
  }
  const doc = new DOMParser().parseFromString(html, 'text/html')
  const spans = doc.body.querySelectorAll('span.mention')
  if (!spans.length) {
    return html
  }
  // Document order matters: once a tag becomes "@<UID>" text, the next span's glue check sees those digits.
  for (const span of spans) {
    const uid = span.getAttribute('data-uid')
    const isValidUid = uid !== null && /^\d+$/.test(uid)
    span.replaceWith(doc.createTextNode(isValidUid && !isGlued(span) ? `@${uid}` : span.textContent ?? ''))
  }
  return doc.body.innerHTML
}

// A tag flush against a word character, "@" or "/" would no longer read as that tag once saved: "@900001" plus a "5"
// is a different UID, and "x@900001" is no tag at all. This mirrors USER_TAG_PATTERN's lookbehind and \b, so such a
// span saves as its name text instead. An element next to the span (or nothing) is a boundary, as it is in the stored
// HTML, where the backend reads the "<" or ">" as a non-word character.
function isGlued(span: Element): boolean {
  return /[\w@/]$/.test(adjacentText(span, 'previous')) || /^\w/.test(adjacentText(span, 'next'))
}

// The text right beside a node within its parent, or '' when an element or the parent's edge comes first. Empty text
// nodes (left behind by unwrapping an empty span) are skipped, since they add nothing between the two.
function adjacentText(node: Node, direction: 'previous' | 'next'): string {
  const step = (from: Node) => direction === 'previous' ? from.previousSibling : from.nextSibling
  let sibling = step(node)
  while (sibling && sibling.nodeType === Node.TEXT_NODE && !(sibling as Text).data) {
    sibling = step(sibling)
  }
  return sibling?.nodeType === Node.TEXT_NODE ? (sibling as Text).data : ''
}
