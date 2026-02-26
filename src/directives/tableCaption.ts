import type {DirectiveBinding, ObjectDirective} from 'vue'
import type {ElWithObserver} from '@/lib/types'

type CaptionBindingValue =
  | string
  | {
      text?: string
      id?: string
    }

function normalizeValue(value: CaptionBindingValue | undefined) {
  if (!value) return {text: ''}
  return typeof value === 'string' ? {text: value} : value
}

function upsertCaption(rootEl: HTMLElement, value: {text?: string; id?: string}): boolean {
  const table = rootEl.querySelector('table')
  if (!table) return false

  // Caption must be a direct child of <table>
  let caption = table.querySelector(':scope > caption') as HTMLTableCaptionElement | null

  if (!caption) {
    caption = document.createElement('caption')
    caption.className = 'sr-only'
    table.insertBefore(caption, table.firstElementChild)
  }

  if (value.id) caption.id = value.id

  const next = (value.text ?? '').trim()
  caption.textContent = next.length ? next : 'Data table'

  return true
}

export const tableCaption: ObjectDirective = {
  mounted(el: ElWithObserver, binding: DirectiveBinding<CaptionBindingValue>) {
    const value = normalizeValue(binding.value)

    if (upsertCaption(el, value)) return

    const observer = new MutationObserver(() => {
      if (upsertCaption(el, value)) observer.disconnect()
    })

    observer.observe(el, {childList: true, subtree: true})
    el.__observer = observer
  },

  updated(el: ElWithObserver, binding: DirectiveBinding<CaptionBindingValue>) {
    const value = normalizeValue(binding.value)
    upsertCaption(el, value)
  },

  unmounted(el: ElWithObserver) {
    el.__observer?.disconnect()
    delete el.__observer
  }
}
