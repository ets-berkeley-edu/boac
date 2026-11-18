import {
  type DataProcessor,
  HtmlDataProcessor,
  type MatcherPattern,
  Plugin,
  type ViewDocument,
  type ViewDocumentFragment
} from 'ckeditor5'
import {fromEditorHtml, toEditorHtml} from '@/lib/user-tags'

/*
* Changes the format the editor stores, the same way CKEditor's Markdown plugin does. The editor reads and writes bodies
* with tags as plain "@<UID>", while inside the editor a tag is a mention span (see MentionUid). It does this by replacing
* the data processor, so editor.data.get() and editor.data.set() speak "@<UID>". The clipboard is untouched: it uses
* editor.data.htmlProcessor, a separate object, so copy and paste keep working with plain HTML and mention spans.
*/

type NameFor = (uid: string) => string | null | undefined

// Wraps an HTML data processor and runs the "@<UID>" conversion on its input and output.
class UserTagDataProcessor implements DataProcessor {
  private readonly html: HtmlDataProcessor

  // nameFor is a getter, not a value, so each load asks for the lookup as it is right now. The editor's config can hand
  // out a new function after the editor starts, and a stale reference would keep using the old one.
  constructor(viewDocument: ViewDocument, private readonly nameFor: () => NameFor | undefined) {
    this.html = new HtmlDataProcessor(viewDocument)
  }

  // Stored body to view. A body with no lookup available converts nothing, so its "@<UID>" text loads as typed.
  toView(data: string): ViewDocumentFragment {
    return this.html.toView(toEditorHtml(data, uid => this.nameFor()?.(uid)))
  }

  // View to stored body: serialize to HTML as usual, then turn each mention span into "@<UID>".
  toData(viewFragment: ViewDocumentFragment): string {
    return fromEditorHtml(this.html.toData(viewFragment))
  }

  // The data controller calls these on the active processor, so they go to the wrapped HTML processor, which owns the
  // DOM converter that reads them.
  registerRawContentMatcher(pattern: MatcherPattern): void {
    this.html.registerRawContentMatcher(pattern)
  }

  useFillerType(type: 'default' | 'marked'): void {
    this.html.useFillerType(type)
  }
}

export default class UserTagData extends Plugin {
  static get pluginName() {
    return 'UserTagData'
  }

  // Set in the constructor, not init(), so the processor is in place before the editor loads its initial data. Plugins
  // are constructed and initialized before editor.data.init() runs.
  constructor(editor: ConstructorParameters<typeof Plugin>[0]) {
    super(editor)
    editor.data.processor = new UserTagDataProcessor(editor.data.viewDocument, () => {
      // The name lookup RichTextEditor puts in config. Read on every call; unset means no conversion happens.
      const nameFor = editor.config.get('userTags.nameFor')
      return typeof nameFor === 'function' ? nameFor as NameFor : undefined
    })
  }
}
