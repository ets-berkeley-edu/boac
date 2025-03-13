<template>
  <div :id="`${idPrefix}-container`">
    <component
      :is="isAutocomplete ? 'v-autocomplete' : 'v-combobox'"
      :id="`${idPrefix}-input`"
      ref="container"
      v-model="model"
      :aria-required="required"
      :autocomplete="autocomplete"
      :base-color="color"
      bg-color="surface"
      :class="clazz"
      :clearable="clearable"
      :color="color"
      :debounce="500"
      :density="density"
      :disabled="disabled"
      hide-details
      hide-no-data
      :items="items"
      :list-props="{ariaLive: 'off'}"
      :loading="isBusy"
      :maxlength="maxlength"
      :menu-icon="null"
      :menu-props="mergedMenuProps"
      :min-width="minWidth"
      :no-filter="isAutocomplete"
      persistent-clear
      :placeholder="placeholder || label"
      return-object
      :type="inputType"
      variant="outlined"
      @blur.stop.prevent="onBlur"
      @keydown.enter.stop.prevent="onSubmit"
      @update:focused="onFocusInput"
      @update:menu="onToggleMenu"
      @update:search="onUpdateSearch"
    >
      <template #loader="{isActive}">
        <v-progress-circular
          v-if="isActive"
          class="mr-5"
          color="primary"
          indeterminate
          size="x-small"
          width="2"
        />
      </template>
      <template #clear>
        <v-btn
          v-if="!isBusy"
          :id="`${idPrefix}-clear-btn`"
          :aria-label="`Clear ${label} input`"
          class="d-flex align-self-center v-icon"
          :class="{'disabled-opacity': !model}"
          density="compact"
          :disabled="!model"
          exact
          :icon="mdiCloseCircle"
          :ripple="false"
          variant="text"
          @keydown.enter.stop.prevent="onClearInput"
          @click.stop.prevent="onClearInput"
        />
      </template>
      <template #item="{index, item}">
        <v-list-item
          :id="`${idPrefix}-option-${index}`"
          :aria-selected="index === focusedListItemIndex"
          class="font-size-18"
          @click="() => onSelectItem(item)"
          @focus="e => onFocusListItem(e, index)"
        >
          <span v-html="highlightQuery(item.props.title)" />
        </v-list-item>
      </template>
      <template v-if="isAutocomplete" #selection="{item}">
        <span v-html="highlightQuery(item.props.title)" />
      </template>
    </component>
  </div>
  <span aria-live="polite" class="sr-only">{{ resultsSummary }}</span>
</template>

<script setup>
import {filter, get, includes, isEmpty} from 'lodash'
import {mdiCloseCircle} from '@mdi/js'
import {nextTick, onMounted, ref} from 'vue'
import {alertScreenReader, escapeForRegExp, pluralize, putFocusNextTick} from '@/lib/utils'

const props = defineProps({
  ariaDescription: {
    default: 'Expect auto-suggest.',
    required: false,
    type: String
  },
  autocomplete: {
    default: 'list',
    required: false,
    type: String
  },
  clazz: {
    default: '',
    required: false,
    type: [String, Object]
  },
  clearable: {
    required: true,
    type: Boolean
  },
  color: {
    default: 'on-surface',
    required: false,
    type: String
  },
  density: {
    default: 'comfortable',
    required: false,
    type: String
  },
  disabled: {
    required: false,
    type: Boolean
  },
  filterResults: {
    default: () => {},
    required: false,
    type: Function
  },
  getValue: {
    required: true,
    type: Function
  },
  idPrefix: {
    required: true,
    type: String
  },
  inputType: {
    default: 'text',
    required: false,
    type: String
  },
  isAutocomplete: {
    required: false,
    type: Boolean
  },
  isBusy: {
    required: false,
    type: Boolean
  },
  items: {
    required: true,
    type: Array
  },
  label: {
    required: true,
    type: String
  },
  listLabel: {
    required: true,
    type: String
  },
  maxlength: {
    default: undefined,
    required: false,
    type: [String, Number]
  },
  menuProps: {
    default: () => {},
    required: false,
    type: Object
  },
  minWidth: {
    default: undefined,
    required: false,
    type: [String, Number]
  },
  onClear: {
    default: () => {},
    required: false,
    type: Function
  },
  onToggleMenu: {
    default: () => {},
    required: false,
    type: Function
  },
  onSubmit: {
    default: () => {},
    required: false,
    type: Function
  },
  onUpdateFocused: {
    default: () => {},
    required: false,
    type: Function
  },
  openOnFocus: {
    required: false,
    type: Boolean
  },
  placeholder: {
    default: undefined,
    required: false,
    type: String
  },
  required: {
    required: false,
    type: Boolean
  },
  setValue: {
    required: true,
    type: Function
  },
  whenItemSelected: {
    default: () => {},
    required: false,
    type: Function
  }
})

const container = ref()
const focusedListItemIndex = ref(undefined)
const mergedMenuProps = ref({})
const model = defineModel({
  get() {
    return props.getValue()
  },
  set(v) {
    props.setValue(v)
  },
  type: String
})
const query = ref(undefined)
const resultsSummary = ref(undefined)
const resultsSummaryInterval = ref(undefined)

onMounted(() => {
  const combobox = getComboboxElement()
  if (combobox) {
    combobox.removeAttribute('role')
    combobox.removeAttribute('aria-expanded')
  }
  const input = getInputElement()
  if (input) {
    input.setAttribute('role', 'combobox')
    input.setAttribute('aria-autocomplete', 'list')
    input.setAttribute('aria-controls', `${props.idPrefix}-menu`)
    input.setAttribute('aria-expanded', false)
    input.setAttribute('aria-label', props.label)
  }
  mergedMenuProps.value = {
    id: `${props.idPrefix}-menu`,
    closeOnContentClick: true,
    ...props.menuProps
  }
})

const getComboboxElement = () => {
  const container = document.getElementById(`${props.idPrefix}-container`)
  return container ? container.querySelector('[role=\'combobox\']') : null
}

const getInputElement = () => {
  return document.getElementById(`${props.idPrefix}-input`)
}

const highlightQuery = suggestion => {
  if (suggestion) {
    const regex = new RegExp(escapeForRegExp(query.value), 'i')
    const match = suggestion.match(regex)
    if (!match) {
      return suggestion
    }
    const matchedText = suggestion.substring(match.index, match.index + match[0].toString().length)
    return suggestion.replace(regex, `<strong>${matchedText}</strong>`)
  }
}

const onBlur = () => {
  const input = getInputElement()
  input.removeAttribute('aria-activedescendant')
  focusedListItemIndex.value = null
  if (isEmpty(query.value)) {
    props.onClear()
  }
}

const onClearInput = () => {
  model.value = null
  props.onClear()
  alertScreenReader('Cleared.')
  putFocusNextTick(`${props.idPrefix}-input`)
}

const onFocusInput = isFocused => {
  if (isFocused) {
    const input = getInputElement()
    input.removeAttribute('aria-activedescendant')
    focusedListItemIndex.value = null
    // Passing open-on-focus via menuProps (https://vuetifyjs.com/en/api/v-menu/#props-open-on-focus)
    // doesn't seem to have an effect, thus this workaround.
    if (props.openOnFocus && !container.value.menu) {
      container.value.menu = true
    }
  }
  props.onUpdateFocused(isFocused)
}

const onFocusListItem = (event, index) => {
  const input = getInputElement()
  input.setAttribute('aria-activedescendant', event.target.id)
  focusedListItemIndex.value = index
}

const onSelectItem = item => {
  model.value = get(item.raw, 'value', item.raw)
  if (props.isAutocomplete) {
    container.value.search = ''
  }
  nextTick(props.whenItemSelected)
}

const onToggleMenu = isOpen => {
  props.onToggleMenu(isOpen)
  nextTick(() => {
    const input = getInputElement()
    if (isOpen) {
      const menu = document.getElementById(`${props.idPrefix}-menu`)
      const listbox = menu && menu.querySelector('[role="listbox"]')
      if (listbox) {
        listbox.setAttribute('aria-label', props.listLabel)
      }
      input.setAttribute('aria-expanded', true)
    } else {
      input.setAttribute('aria-expanded', false)
      input.removeAttribute('aria-activedescendant')
      clearInterval(resultsSummaryInterval.value)
    }
  })
}

const onUpdateSearch = q => {
  query.value = q
  props.filterResults(q)
  clearInterval(resultsSummaryInterval.value)
  resultsSummaryInterval.value = setInterval(setResultsSummary, 1000)
}

const setResultsSummary = () => {
  const menuOverlay = document.getElementById(`${props.idPrefix}-menu`)
  const listbox = menuOverlay && menuOverlay.querySelector('[role="listbox"]')
  clearInterval(resultsSummaryInterval.value)
  if (listbox) {
    const suggestions = filter(listbox.children, child => includes(child.classList, 'v-list-item'))
    resultsSummary.value = pluralize('result', suggestions.length)
  } else {
    resultsSummary.value = ''
  }
}
</script>

<style scoped>
:deep(.v-field__loader) {
  display: flex;
  align-items: center;
  height: 100%;
  justify-content: flex-end;
  padding-right: 1px;
  top: 0;
}
:deep(.v-field) {
  color: inherit !important;
}
</style>
