import './main.scss'
import {aliases, mdi} from 'vuetify/iconsets/mdi-svg'
import {createVuetify} from 'vuetify'
import {Intersect, Resize} from 'vuetify/directives'
import {VAlert} from 'vuetify/components/VAlert'
import {VAppBar, VAppBarTitle} from 'vuetify/components/VAppBar'
import {VApp} from 'vuetify/components/VApp'
import {VAutocomplete} from 'vuetify/components/VAutocomplete'
import {VBtn} from 'vuetify/components/VBtn'
import {VCard, VCardActions, VCardSubtitle, VCardText, VCardTitle} from 'vuetify/components/VCard'
import {VCheckbox} from 'vuetify/components/VCheckbox'
import {VChip} from 'vuetify/components/VChip'
import {VCol, VContainer, VSpacer, VRow} from 'vuetify/components/VGrid'
import {VDataTable, VDataTableVirtual} from 'vuetify/components/VDataTable'
import {VDialog} from 'vuetify/components/VDialog'
import {VExpansionPanel, VExpansionPanels, VExpansionPanelText, VExpansionPanelTitle} from 'vuetify/components/VExpansionPanel'
import {VFileInput} from 'vuetify/components/VFileInput'
import {VIcon} from 'vuetify/components/VIcon'
import {VImg} from 'vuetify/components/VImg'
import {VList, VListItem, VListItemAction, VListItemSubtitle, VListItemTitle} from 'vuetify/components/VList'
import {VMain} from 'vuetify/components/VMain'
import {VMenu} from 'vuetify/components/VMenu'
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
    VBtn,
    VCard,
    VCardActions,
    VCardSubtitle,
    VCardText,
    VCardTitle,
    VCheckbox,
    VChip,
    VCol,
    VContainer,
    VDataTable,
    VDataTableVirtual,
    VDialog,
    VExpansionPanel,
    VExpansionPanels,
    VExpansionPanelText,
    VExpansionPanelTitle,
    VFileInput,
    VIcon,
    VImg,
    VList,
    VListItem,
    VListItemAction,
    VListItemSubtitle,
    VListItemTitle,
    VMain,
    VMenu,
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
          body: '#212529',
          'btn-secondary': '#6c757d',
          gray: '#cccccc',
          error: '#cf1715',
          info: '#367DA1',
          'pale-blue': '#f3fbff',
          primary: '#337ab7',
          red: colors.red.darken1,
          secondary: '#8bbdda',
          success: '#437F4B',
          warning: '#f0ad4e'
        }
      }
    }
  }
})
