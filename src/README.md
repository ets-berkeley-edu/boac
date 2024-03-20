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

TODO: notes

### b-collapse to v-expansion-panels

- `<v-expansion-panels>` are an accordion-style component. For a simple collapsible section controlled by a separate button, use `<v-expand-transition>` instead.
- Replace `<b-collapse v-model>` with `<v-expansion-panels v-model><v-expansion-panel>`.
- Use `v-model` if you need to open or close the panels programmatically. Give each `<v-expansion-panel>` a `value`; `v-model` aray will contain the `value` of each expanded panel (see https://vuetifyjs.com/en/components/expansion-panels/#model).

### b-dropdown to v-select

Example: src/components/note/CreateNoteHeader.vue

- VSelect has no direct equivalent of `<b-select-header>`; use Vuetify's `prepend-item` slot instead.
- Unlike `<b-dropdown>`, `<v-select>` shows the selected option in place of the label. Keep the label from disappearing when an option is selected by adding property `persistent-hint`.

### b-modal to v-overlay

- Add property `persistent` so the overlay stays open when you click outside.
- Add property e.g. `:menu-props="{contentClass: 'bg-white'}"` to override the default gray background of the menu.
- Add `<v-card class="modal-content">` as a child of `<v-overlay>` and wrapping its contents.
- Remove these properties: `body-class`, `hide-footer`, and `hide-header`.

### b-table to v-table

Example: src/components/search/SortableStudents.vue

- VDataTableVirtual seems to be the only way to get rid of VDataTable's default pagination.
- Vuetify tables are not automatically responsive like Bootstrap tables. The `stacked_table` class in global.scss attempts to replicate Bootstrap's behavior. It can be applied conditionally using the `v-resize` directive.
- In Vuetify tables with sortable headers, the default table headers need to be overridden so that they contain buttons for the benefit of screen readers.

### b-popover to v-tooltip

TODO: notes
