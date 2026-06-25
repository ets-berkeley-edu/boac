// This file is for Safari-specific workarounds for menu/combobox keyboard focus.
//
// 1. Safari does not move focus to <button> elements on click. Vuetify's menu
//    arrow-key navigation expects the activator to hold focus when the menu
//    opens, so without this focus never enters the menu and arrow keys escape.
// 2. Vuetify 3.11 adds `aria-owns` to menu/combobox activators,
//    which Safari mishandles and interferes with focus routing.
//    We have to manually remove it in Safari. An alternative fix to this would be to go back to Vuetify 3.10.
//
// Chrome/Firefox should remain unaffected as we check if the browser is Safari first.

// Detect Apple WebKit (Safari on macOS/iOS, and iOS browsers that use WebKit).
// Prefer User-Agent Client Hints when available, otherwisefall back to UA parsing (which is not that reliable).
// This link is helpful https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Browser_detection_using_the_user_agent
type NavigatorWithUAData = Navigator & {
  userAgentData?: {
    brands?: Array<{brand: string}>
  }
}

export const isSafari = (): boolean => {
  if (typeof navigator === 'undefined') {
    return false
  }
  const nav = navigator as NavigatorWithUAData
  const brands = nav.userAgentData?.brands
  if (brands?.length) {
    const isChromium = brands.some(({brand}) =>
      /Chromium|Google Chrome|Microsoft Edge|Opera|Brave/i.test(brand)
    )
    if (isChromium) {
      return false
    }
    return brands.some(({brand}) => brand.includes('Safari'))
  }
  const {userAgent} = navigator
  return /AppleWebKit/i.test(userAgent) &&
    !/Chrome|Chromium|Edg\/|OPR\//i.test(userAgent)
}

const observedElements = new WeakSet<HTMLElement>()

export const stripSafariAriaOwns = (el: HTMLElement): MutationObserver | undefined => {
  if (!isSafari() || observedElements.has(el)) {
    return undefined
  }
  observedElements.add(el)
  el.removeAttribute('aria-owns')
  const observer = new MutationObserver(mutations => {
    for (const m of mutations) {
      if (m.attributeName === 'aria-owns') {
        el.removeAttribute('aria-owns')
      }
    }
  })
  observer.observe(el, {attributes: true, attributeFilter: ['aria-owns']})
  return observer
}

// Bind to an activator's @mousedown. Safari-only: forces the activator to take
// focus on click and strips aria-owns (which vuetify added in 3.11)
export const onSafariActivatorMousedown = (e: MouseEvent): void => {
  if (!isSafari()) {
    return
  }
  const el = e.currentTarget as HTMLElement | null
  if (el) {
    el.focus()
    stripSafariAriaOwns(el)
  }
}

// Vuetify's arrow navigation only fires when focus sits on the
// activator button or inside the v-list, but Safari does not move focus to
// buttons/list-items on mouse click.
//
// Attaching a *document-level* capture listener while the menu is open, so arrows are caught
// regardless of where focus landed, and we move focus between items directly.

const MENU_ITEM_SELECTOR = [
  '[role="menuitemcheckbox"]:not([aria-disabled="true"])',
  '[role="menuitemradio"]:not([aria-disabled="true"])',
  '[role="menuitem"]:not([aria-disabled="true"])',
  'button:not([disabled])'
].join(', ')

const getSafariMenuFocusables = (menuId: string): HTMLElement[] => {
  const menu = document.getElementById(menuId)
  if (!menu) {
    return []
  }
  return Array.from(menu.querySelectorAll(MENU_ITEM_SELECTOR)) as HTMLElement[]
}

// Safari does not apply :focus-visible to programmatically-focused elements,
// so Vuetify's focus styling never appears.
// This adds aclass (see .safari-menu-focus-visible in global.css) to show focus visibly.
const FOCUS_CLASS = 'safari-menu-focus-visible'

const focusMenuItemAt = (items: HTMLElement[], index: number): void => {
  items.forEach(item => item.classList.remove(FOCUS_CLASS))
  const el = items[index]
  if (el) {
    el.classList.add(FOCUS_CLASS)
    el.focus()
    el.scrollIntoView({block: 'nearest'})
  }
}

const menuKeydownHandlers = new Map<string, (e: KeyboardEvent) => void>()

// Call when a role="menu" overlay opens. Safari-only: focuses the first item
// and starts intercepting ArrowUp/ArrowDown for roving focus.
export const onSafariMenuOpen = (menuId: string): void => {
  if (!isSafari()) {
    return
  }
  requestAnimationFrame(() => focusMenuItemAt(getSafariMenuFocusables(menuId), 0))
  if (menuKeydownHandlers.has(menuId)) {
    return
  }
  const handler = (e: KeyboardEvent): void => {
    if (e.key !== 'ArrowDown' && e.key !== 'ArrowUp') {
      return
    }
    const items = getSafariMenuFocusables(menuId)
    if (!items.length) {
      return
    }
    e.preventDefault()
    e.stopImmediatePropagation()
    const active = document.activeElement as HTMLElement | null
    const index = items.findIndex(item => item === active || item.contains(active))
    const nextIndex = e.key === 'ArrowDown'
      ? Math.min(index + 1, items.length - 1)
      : Math.max(index - 1, 0)
    focusMenuItemAt(items, nextIndex)
  }
  document.addEventListener('keydown', handler, true)
  menuKeydownHandlers.set(menuId, handler)
}

// Call when the role="menu" overlay closes (and on component unmount).
export const onSafariMenuClose = (menuId: string): void => {
  const handler = menuKeydownHandlers.get(menuId)
  if (handler) {
    document.removeEventListener('keydown', handler, true)
    menuKeydownHandlers.delete(menuId)
  }
  getSafariMenuFocusables(menuId).forEach(item => item.classList.remove(FOCUS_CLASS))
}
