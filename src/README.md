# Face/Off: Old vs. New

<img alt="Face/Off movie poster" src="assets/font-awesome-and-mdi-faceoff.png" width="360" />

## Icons
Font Awesome to MDI

| <span style="color: yellow">Font Awesome</span> | <span style="color: pink">MDI Icons</span> |
|-------------------------------------------------|--------------------------------------------|
| address-card                                    | mdiContacts                                |
| angle-down                                      | mdiTriangleSmallDown                       |
| bug                                             | mdiBug                                     |
| calendar-minus                                  | mdiCalendarMinus                           |
| caret-down                                      | mdiMenuDown                                |
| caret-right                                     | mdiMenuRight                               |
| caret-up                                        | mdiMenuUp                                  |
| chart-pie                                       | mdiChartPie                                |
| check                                           | mdiCheckBold                               |
| check-circle                                    | mdiCheckCircleOutline                      |
| check-square                                    | mdiCheckboxMarkedOutline                   |
| circle                                          | mdiCircleOutline                           |
| clock                                           | mdiClockOutline                            |
| copy                                            | mdiContentCopy                             |
| edit                                            | mdiNoteEditOutline                         |
| envelope                                        | mdiEmail                                   |
| exclamation                                     | mdiExclamation                             |
| exclamation-triangle                            | mdiAlertRhombus                            |
| external-link-alt                               | mdiOpenInNew                               |
| file-alt                                        | mdiFileOutline                             |
| graduation-cap                                  | mdiSchool                                  |
| grip-vertical                                   | mdiDrag                                    |
| info-circle                                     | mdiInformationOutline                      |
| link                                            | mdiLinkVariant                             |
| list                                            | mdiFormatListBulleted                      |
| long-arrow-alt-down                             | mdiArrowDownThin                           |
| long-arrow-alt-up                               | mdiArrowUpThin                             |
| minus                                           | mdiMinusThick                              |
| paperclip                                       | mdiPaperclip                               |
| plane-departure                                 | mdiAirplaneTakeoff                         |
| play-circle                                     | mdiPlayCircleOutline                       |
| plus                                            | mdiPlus                                    |
| plus-square                                     | mdiPlusBox                                 |
| print                                           | mdiPrinterOutline                          |
| sign-in-alt                                     | mdiLoginVariant                            |
| sliders-h                                       | mdiTune                                    |
| spinner                                         | v-progress-circular                        |
| square                                          | mdiSquare                                  |
| square (far)                                    | mdiSquareOutline                           |
| star (far)                                      | mdiStarOutline                             |
| sticky-note (far)                               | mdiNoteOutline                             |
| sync                                            | mdiSync                                    |
| table                                           | mdiTable                                   |
| times                                           | mdiClose                                   |
| times-circle                                    | mdiCloseCircleOutline                      |
| toggle-off                                      | v-switch                                   |
| toggle-on                                       | v-switch                                   |
| trash-alt                                       | mdiTrashCanOutline                         |
| trash-restore                                   | mdiDeleteRestore                           |
| user-circle                                     | mdiAccountCircle                           |


## <span style="color: purple">BootstrapVue</span> to <span style="color: green">Vuetify</span>

<img src="assets/migrating-ducks.png" width="360">

### b-btn to v-btn

* change variant `link` to variant `text`
* `variant="primary"` becomes `color="primary"`

### b-form-checkbox to v-checkbox

* If 'switch' is true then use `<v-switch />`
* Don't forget to `hide-details`

### b-form-input to v-text-field

* Add property `variant="outlined"`
** If the field is on a colored background, add `bg-color="white"`
* The default `density` has a lot of padding. Consider using `density="comfortable"` or `density="compact"`

### b-form-textarea to v-textarea

* Use `variant="outlined"`

### b-link to ???

TODO: notes

### b-collapse to v-expansion-panels

- `<v-expansion-panels>` are an accordion-style component. For a simple collapsible section controlled by a separate button, use `<v-expand-transition>` instead.
- Replace `<b-collapse v-model>` with `<v-expansion-panels v-model><v-expansion-panel>`.
- Use `v-model` if you need to open or close the panels programmatically. Give each `<v-expansion-panel>` a `value`; `v-model` aray will contain the `value` of each expanded panel (see https://vuetifyjs.com/en/components/expansion-panels/#model).

### b-dropdown to select

Example: src/components/note/AdvisingNoteTopics.vue

Do NOT use Vuetify `<v-select />` component because it violates web accessibility. Use a native `<select />` HTML element.

### b-link to (1) native anchor tag or (2) v-btn with variant 'text'

TODO: Notes

### b-table-lite to v-data-table

If the code is difficult to migrate then consider converting it to a generic `<table />` without using Vuetify at all.

See https://vuetifyjs.com/en/api/v-data-table/#links

* `fields` becomes `headers` (therein, `label` becomes `title`)

### b-modal to v-dialog

- Add property `persistent` so the overlay stays open when you click outside.
- Add property e.g. `:menu-props="{contentClass: 'bg-white'}"` to override the default gray background of the menu.
- Add `<v-card class="modal-content">` as a child of `<v-dialog>` and wrapping its contents.
- If specifying `width`, `max-width`, or `min-width`, put these properties on the `<v-card>` and not on `<v-dialog`>.
- Remove these properties: `body-class`, `hide-footer`, and `hide-header`.
- Use `<v-card-title>`, `<v-card-text class="modal-body">`, and `<v-card-actions class="modal-footer">` so that every dialog has consistent padding.
- Add `aria-labelledby=<id of header>` and optionally `aria-describedby=<id of content explaining the purpose of the dialog>`.
- When the dialog opens, focus should land on the first interactive element if one exists, or the button to close the dialog.
- When the dialog closes, focus should land on the element that triggered it to open.
- See AreYouSureModal.vue for a simple example.

### b-table to v-table

Example: src/components/search/SortableStudents.vue

- VDataTableVirtual seems to be the only way to get rid of VDataTable's default pagination.
- Vuetify tables are not automatically responsive like Bootstrap tables. The `stacked_table` class in global.scss attempts to replicate Bootstrap's behavior. It can be applied conditionally using the `v-resize` directive.
- In Vuetify tables with sortable headers, the default table headers need to be overridden so that they contain buttons for the benefit of screen readers.
- To highlight rows when you hover over them, add class `.table-hover`.

### b-table-simple to (1) native table or (2) v-data-table

A native table may be easier to style. Or, use `v-data-table` with header and item slots.

### b-popover to v-tooltip

- Replace property `placement` with `location`.

### b-toggle to v-expansion-panels, with v-btn to trigger

TODO: notes

## Web Accessibility

How code and verify the front-end, with accessibility always in mind:

* Use the BOA feature with keyboard-only.
