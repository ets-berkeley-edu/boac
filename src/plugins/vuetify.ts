import './main.scss'
import {aliases, mdi} from 'vuetify/iconsets/mdi-svg'
import {createVuetify} from 'vuetify'
import {Intersect, Resize} from 'vuetify/directives'
import {VAlert} from 'vuetify/components/VAlert'
import {VAppBar, VAppBarTitle} from 'vuetify/components/VAppBar'
import {VApp} from 'vuetify/components/VApp'
import {VAutocomplete} from 'vuetify/components/VAutocomplete'
import {VBanner} from 'vuetify/components/VBanner'
import {VBtn} from 'vuetify/components/VBtn'
import {VBtnToggle} from 'vuetify/components/VBtnToggle'
import {VCard, VCardActions, VCardSubtitle, VCardText, VCardTitle} from 'vuetify/components/VCard'
import {VCheckbox} from 'vuetify/components/VCheckbox'
import {VChip} from 'vuetify/components/VChip'
import {VCol, VContainer, VSpacer, VRow} from 'vuetify/components/VGrid'
import {VCombobox} from 'vuetify/components/VCombobox'
import {VDataTable, VDataTableVirtual} from 'vuetify/components/VDataTable'
import {VDateInput} from 'vuetify/labs/VDateInput'
import {VDialog} from 'vuetify/components/VDialog'
import {VDivider} from 'vuetify/components/VDivider'
import {VExpandTransition, VFadeTransition} from 'vuetify/components/transitions'
import {VExpansionPanel, VExpansionPanels, VExpansionPanelText, VExpansionPanelTitle} from 'vuetify/components/VExpansionPanel'
import {VFileInput} from 'vuetify/components/VFileInput'
import {VFooter} from 'vuetify/components/VFooter'
import {VIcon} from 'vuetify/components/VIcon'
import {VImg} from 'vuetify/components/VImg'
import {VLayout} from 'vuetify/components/VLayout'
import {VList, VListItem, VListItemAction, VListItemSubtitle, VListItemTitle} from 'vuetify/components/VList'
import {VMain} from 'vuetify/components/VMain'
import {VMenu} from 'vuetify/components/VMenu'
import {VNavigationDrawer} from 'vuetify/components/VNavigationDrawer'
import {VOverlay} from 'vuetify/components/VOverlay'
import {VProgressCircular} from 'vuetify/components/VProgressCircular'
import {VRadio} from 'vuetify/components/VRadio'
import {VRadioGroup} from 'vuetify/components/VRadioGroup'
import {VSelect} from 'vuetify/components/VSelect'
import {VTable} from 'vuetify/components/VTable'
import {VTextarea} from 'vuetify/components/VTextarea'
import {VTextField} from 'vuetify/components/VTextField'
import {VTooltip} from 'vuetify/components/VTooltip'

// @ts-ignore
import colors from 'vuetify/lib/util/colors'

export default createVuetify({
  components: {
    VApp,
    VAppBar,
    VAppBarTitle,
    VAlert,
    VAutocomplete,
    VBanner,
    VBtn,
    VBtnToggle,
    VCard,
    VCardActions,
    VCardSubtitle,
    VCardText,
    VCardTitle,
    VCheckbox,
    VChip,
    VCol,
    VCombobox,
    VContainer,
    VDataTable,
    VDataTableVirtual,
    VDateInput,
    VDialog,
    VDivider,
    VExpandTransition,
    VExpansionPanel,
    VExpansionPanels,
    VExpansionPanelText,
    VExpansionPanelTitle,
    VFadeTransition,
    VFileInput,
    VFooter,
    VIcon,
    VImg,
    VLayout,
    VList,
    VListItem,
    VListItemAction,
    VListItemSubtitle,
    VListItemTitle,
    VMain,
    VMenu,
    VNavigationDrawer,
    VOverlay,
    VProgressCircular,
    VRadio,
    VRadioGroup,
    VRow,
    VSelect,
    VSpacer,
    VTable,
    VTextarea,
    VTextField,
    VTooltip
  },
  defaults: {
    VBtn: {
      style: 'text-transform: none;',
    }
  },
  directives: {
    Intersect,
    Resize
  },
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi
    }
  },
  theme: {
    themes: {
      light: {
        colors: {
          'accent-green': '#36a600',
          alert: '#fef6e6',
          anchor: '#337ab7',
          body: '#212529',
          'btn-secondary': '#6c757d',
          gold: '#857103',
          error: '#cf1715',
          faint: '#e0e0e0',
          info: '#367da1',
          'light-blue': '#c0ecff',
          'light-yellow': '#ffecc0',
          'pale-blue': '#f3fbff',
          primary: '#3b7ea5',
          quaternary: '#083456',
          red: colors.red.darken1,
          secondary: '#96C3de',
          'sky-blue': '#e3f5ff',
          success: '#437f4b',
          tertiary: '#125074',
          warning: colors.orange.accent4
        }
      }
    }
  }
})
