import 'vuetify/styles'
import {aliases, mdi} from 'vuetify/iconsets/mdi-svg'
import {createVuetify} from 'vuetify'
import {VAppBar, VAppBarTitle} from 'vuetify/components/VAppBar'
import {VApp} from 'vuetify/components/VApp'
import {VAutocomplete} from 'vuetify/components/VAutocomplete'
import {VBtn} from 'vuetify/components/VBtn'
import {VCard, VCardActions, VCardSubtitle, VCardText, VCardTitle} from 'vuetify/components/VCard'
import {VCol, VContainer, VSpacer, VRow} from 'vuetify/components/VGrid'
import {VDatePicker} from 'vuetify/components/VDatePicker'
import {VDialog} from 'vuetify/components/VDialog'
import {VExpansionPanel, VExpansionPanels, VExpansionPanelText, VExpansionPanelTitle} from 'vuetify/components/VExpansionPanel'
import {VIcon} from 'vuetify/components/VIcon'
import {VImg} from 'vuetify/components/VImg'
import {VList, VListItem, VListItemAction, VListItemSubtitle, VListItemTitle} from 'vuetify/components/VList'
import {VMain} from 'vuetify/components/VMain'
import {VMenu} from 'vuetify/components/VMenu'
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
    VApp,
    VAppBar,
    VAppBarTitle,
    VAutocomplete,
    VBtn,
    VCard,
    VCardActions,
    VCardSubtitle,
    VCardText,
    VCardTitle,
    VCol,
    VContainer,
    VDatePicker,
    VDialog,
    VExpansionPanel,
    VExpansionPanels,
    VExpansionPanelText,
    VExpansionPanelTitle,
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
          alert: '#fef6e6',
          error: '#b94a48',
          info: '#367DA1',
          primary: '#337ab7',
          red: colors.red.darken1,
          secondary: '#eee',
          success: '#437F4B'
        }
      }
    }
  }
})
