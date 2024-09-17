import './main.scss'
import {aliases, mdi} from 'vuetify/iconsets/mdi-svg'
import {createVuetify} from 'vuetify'
import {DatePicker} from 'v-calendar'
import {Intersect, Resize} from 'vuetify/directives'
import {VAlert} from 'vuetify/components/VAlert'
import {VAppBar, VAppBarNavIcon, VAppBarTitle} from 'vuetify/components/VAppBar'
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
import {VTable} from 'vuetify/components/VTable'
import {VTextarea} from 'vuetify/components/VTextarea'
import {VTextField} from 'vuetify/components/VTextField'
import {VTooltip} from 'vuetify/components/VTooltip'

// @ts-ignore
import colors from 'vuetify/lib/util/colors'

export default createVuetify({
  components: {
    DatePicker,
    VApp,
    VAppBar,
    VAppBarNavIcon,
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
    VSpacer,
    VTable,
    VTextarea,
    VTextField,
    VTooltip
  },
  defaults: {
    VBtn: {
      style: 'text-transform: none;',
    },
    VTextField: {
      density: 'compact',
      variant: 'outlined'
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
    variations: {
      colors: ['primary', 'warning', 'success'],
      lighten: 0,
      darken: 1
    },
    themes: {
      light: {
        colors: {
          'accent-blue': '#005c91',
          'accent-green': '#36a600',
          'accent-orange': '#e48600',
          'accent-purple': '#b300c5',
          'accent-red': '#d0021b',
          anchor: '#337ab7',
          'anchor-hover': '#0056b3',
          body: '#212529',
          'category-alert': '#eb9d3e',
          'category-appointment': '#eee',
          'category-eForm': '#5fbeb6',
          'category-hold': '#bc74fe',
          'category-note': '#999',
          'category-requirement': '#93c165',
          'chart-boxplot': '#ccc',
          'chart-boxplot-median': '#666',
          'chart-series-1': '#aec9eb',
          'chart-series-2': '#d6e4f9',
          gold: '#826F03',
          grey: '#757575',
          error: '#cf1715',
          info: '#367da1',
          'light-blue': '#c0ecff',
          'light-grey': '#f9f9f9',
          'light-yellow': '#ffecc0',
          'on-category-alert': '#fff',
          'on-category-appointment': '#666',
          'on-category-eForm': '#fff',
          'on-category-hold': '#fff',
          'on-category-requirement': '#fff',
          'pale-blue': '#f3fbff',
          'pale-yellow': '#fef6e6',
          primary: '#3b7ea5',
          quaternary: '#083456',
          red: colors.red.darken1,
          secondary: '#96C3de',
          'service-announcement': '#f0ad4e',
          'sky-blue': '#e3f5ff',
          success: '#437f4b',
          tertiary: '#125074',
          warning: '#f08c00'
        }
      }
    }
  }
})
