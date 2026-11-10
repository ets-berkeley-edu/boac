# src/CLAUDE.md

Guidance for the Vue 3 / TypeScript / Vuetify 3 frontend. The ground rules in the root `CLAUDE.md` (no commits, WCAG 2.2 AA, student-data protection, commenting, final checks) apply here too.

## Conventions

- **Components** use `<script setup>` (with `lang="ts"` in newer files). Match the style of the file or folder you're editing.
- **HTTP calls go through `src/api/`.** Each backend domain has one module (e.g. `src/api/topics.ts`) that builds URLs with `utils.apiBaseUrl()` from `src/api/api-utils.ts` and returns `response.data`. Never call `axios` directly from a component or store. Add a function to the matching module instead.
- **App-wide plumbing** (startup, layouts, router guards, axios error handling, the context store, demo mode, Google Analytics) is described in `.claude/docs/frontend-shell.md`. Read it before adding a page or changing anything app-wide.
- **Shared state lives in Pinia stores** under `src/stores/`. `context.ts` holds the current user, app config, and screen-reader alerts. Multi-step editing flows (notes, cohorts, degree checks, curated groups) have their own store folders, e.g. `src/stores/note-edit-session/`.
- **Permission checks** use the helpers in `src/lib/boa-user.ts`, which mirror the backend decorators. See `.claude/docs/permissions.md`.
- **Shared types** go in `src/lib/types.ts` (or the domain-specific `types-*.ts` files).
- **Reuse the components in `src/components/util/`** before writing new ones. Several of them exist specifically for accessibility (see below).
- **Student data in the UI.** Never hard-code real SIDs, names, or other student data, including in placeholder text and examples.
- **Don't render user input with `v-html`.** Use normal `{{ }}` interpolation, which Vue escapes. Some existing components already use `v-html` on user-entered fields (e.g. in degree progress). Don't copy that pattern into new code. If rich text really must be rendered, it has to be sanitized first, and the developer should know about it.

## Accessibility: WCAG 2.2 AA

Every change must meet WCAG 2.2 AA. Use BOA's existing helpers and patterns rather than inventing new ones, so behavior stays consistent for screen-reader and keyboard users across the app.

### BOA helpers to use

| Need | Use |
|---|---|
| Announce a status change (saved, deleted, loading, results updated) | `alertScreenReader(message)` from `src/lib/utils.ts`. It writes to the `aria-live` region in `App.vue`. |
| Move focus after an action (e.g. opening a form, closing a dialog) | `putFocusNextTick(elementId)` from `src/lib/utils.ts` |
| Set the page title when a view's content loads | `setPageTitle(phrase)` from `src/lib/utils.ts` |
| Finish a page load and move focus to its heading | `contextStore.loadingComplete(focusId)`, passing the id of the page's `<h1>` |
| Hide text visually but keep it for screen readers | the `sr-only` class (`sr-only-focusable` for skip links) |
| Confirmation dialogs | `AreYouSureModal.vue` |
| Modal headers | `ModalHeader.vue` |
| Trapping focus inside a dialog | `FocusLock` from `vue-focus-lock`, as `AreYouSureModal.vue` does |
| Making other (inactive) overlays inert while a modal is open | `toggleModalBackgroundDisabled(isOpen)` |
| Combobox / date entry | `AccessibleCombobox.vue`, `AccessibleDateInput.vue` |
| Sortable table columns | `SortableTableHeader.vue` |

### Rules for every change

- **Names and roles.** Every interactive control has an accessible name a screen reader can announce. Icon-only buttons need `aria-label`. Form inputs need a visible `<label>` tied to them. Use native elements (`<button>`, `<a>`, `<input>`) or Vuetify components before adding ARIA roles to `<div>`s.
- **Keyboard.** Everything that works with a mouse works with the keyboard alone, in a logical tab order. Don't add positive `tabindex` values. `Esc` closes dialogs and menus.
- **Focus.** Focus is always visible. When a dialog opens, focus moves into it. When it closes, focus returns to the control that opened it. After deleting or adding an item, move focus somewhere sensible so it doesn't land on `<body>`.
- **Focus not obscured (2.4.11, new in 2.2).** A focused element must not be hidden behind sticky headers, footers, or banners. The `scroll-margins` class (added automatically by `putFocusNextTick`) helps with this.
- **Target size (2.5.8, new in 2.2).** Clickable and tappable targets are at least 24×24 CSS pixels, or have enough spacing around them.
- **Dragging (2.5.7, new in 2.2).** Anything done by drag-and-drop also has a single-pointer alternative, such as buttons or a menu.
- **Redundant entry and accessible authentication (3.3.7, 3.3.8, new in 2.2).** Don't make users re-enter information they already gave in the same flow. Don't add steps that rely on memorizing or transcribing something.
- **Text resize and reflow.** Layouts must work with text at 200% and at a 320px-wide viewport without losing content or functionality. Use relative units, and avoid fixed heights on containers that hold text. Vuetify's breakpoints (`$vuetify.display`, `useDisplay()`) measure the viewport in pixels and ignore the browser's font-size setting, so when a breakpoint decides whether a layout stacks, compare `useTextScaledDisplayWidth()` from `src/lib/text-scale.ts` against it instead. Don't give Highcharts a `width` in rem: it reads the number as px. `global.css` gives HTML (`useHTML`) tooltips `width: max-content` so their box always fits the text.
- **Color.** Text contrast is at least 4.5:1 (3:1 for large text and for UI components and focus indicators). Color is never the only way information is shown. Pair it with text or an icon.
- **Headings and landmarks.** Each view has one `<h1>`, and heading levels don't skip. Page content sits inside the existing layout landmarks.
- **Dynamic content.** Loading states, validation errors, and search-result counts are announced, either with `alertScreenReader` or an `aria-live` region. Error messages are tied to their inputs with `aria-describedby`.
- **Images.** Informative images have meaningful `alt` text. Decorative images use `alt=""`.
- **Tables.** Data tables use real `<table>` markup with `<th>` and `scope` (or Vuetify data tables, which do this), and a caption or `aria-label`.

When you finish a frontend change, say which of these you checked and anything you couldn't verify without a browser or screen reader.
