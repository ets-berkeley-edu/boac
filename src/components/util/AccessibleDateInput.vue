<template>
  <date-picker
    v-model.date="model"
    :disabled="disabled"
    :input-debounce="500"
    :max-date="maxDate"
    :min-date="minDate"
    :popover="{placement: 'top', visibility: 'focus'}"
    :step="1"
    @did-move="makeCalendarAccessible"
    @dayclick="() => putFocusNextTick(`${idPrefix}-clear-btn`)"
    @daykeydown="(day, e) => onDaykeydown(e)"
    @popover-did-hide="() => isPopoverVisible = false"
    @popover-did-show="onPopoverShown"
    @transition-start="() => onTransitionStart"
  >
    <template #default="{ inputValue, inputEvents }">
      <v-text-field
        :id="inputId"
        :aria-controls="`${idPrefix}-popover`"
        :aria-describedby="ariaDescribedby"
        :aria-expanded="isPopoverVisible"
        aria-haspopup="dialog"
        :aria-required="required"
        autocomplete="off"
        bg-color="white"
        class="date-input"
        clearable
        color="primary"
        :disabled="disabled"
        :error="!isValid(inputValue)"
        haspopup="dialog"
        hide-details
        :model-value="inputValue"
        persistent-clear
        placeholder="MM/DD/YYYY"
        validate-on="blur"
        @click:clear="e => onClickClear(e, inputEvents)"
        @keyup="e => onInputKeyup(e, inputEvents)"
        @mouseleave="inputEvents.mouseleave"
        @mousemove="inputEvents.mousemove"
        @update:focused="hasFocus => onUpdateFocus(hasFocus, inputEvents)"
        @update:model-value="v => onUpdateModel(inputEvents)"
      >
        <template #clear>
          <v-btn
            :id="`${idPrefix}-clear-btn`"
            :aria-label="`Clear ${ariaLabel}`"
            class="d-flex align-self-center v-icon"
            color="primary"
            density="compact"
            :disabled="disabled"
            exact
            :icon="mdiCloseCircle"
            variant="text"
            @click.stop.prevent="e => onClickClear(e, inputEvents)"
          />
        </template>
      </v-text-field>
    </template>
  </date-picker>
</template>

<script setup>
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {computed, nextTick, onMounted, ref} from 'vue'
import {DateTime} from 'luxon'
import {each} from 'lodash'
import {mdiCloseCircle} from '@mdi/js'

const props = defineProps({
  ariaLabel: {
    default: 'date',
    required: false,
    type: String
  },
  ariaDescribedby: {
    default: undefined,
    required: false,
    type: String
  },
  containerId: {
    required: true,
    type: String
  },
  disabled: {
    required: false,
    type: Boolean
  },
  getValue: {
    required: true,
    type: Function
  },
  idPrefix: {
    required: true,
    type: String
  },
  maxDate: {
    default: null,
    required: false,
    type: Date,
  },
  minDate: {
    default: null,
    required: false,
    type: Date,
  },
  required: {
    required: false,
    type: Boolean
  },
  setValue: {
    required: true,
    type: Function
  },
})

const model = defineModel({
  get() {
    return props.getValue()
  },
  set(v) {
    props.setValue(v)
  },
  type: Date
})
const inputId = computed(() => `${props.idPrefix}-input`)
const isPopoverVisible = ref(false)
const popover = ref()

onMounted(() => {
  // Setting this as a prop on the VTextField component breaks the "clear" button.
  document.getElementById(inputId.value).setAttribute('role', 'combobox')
})

const isValid = dateString => {
  if (!dateString || dateString === '') {
    return true
  }
  const date = DateTime.fromFormat(dateString, 'MM/dd/yyyy')
  return date.isValid
}

const makeCalendarAccessible = () => {
  if (!popover.value) {
    return false
  }
  const weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  const nextMonthBtn = popover.value.querySelector('.vc-next')
  const prevMonthBtn = popover.value.querySelector('.vc-prev')
  const srAlert = document.getElementById(`${props.idPrefix}-popover-sr-alert`)
  const title = popover.value.querySelector('.vc-title')
  const weeks = popover.value.querySelector('.vc-weeks')
  const weekdayLabels = popover.value.querySelectorAll('.vc-weekday')
  if (nextMonthBtn) {
    nextMonthBtn.ariaLabel = 'next month'
    nextMonthBtn.id = `${props.idPrefix}-popover-next-month-btn`
  }
  if (prevMonthBtn) {
    prevMonthBtn.ariaLabel = 'previous month'
    prevMonthBtn.id = `${props.idPrefix}-popover-prev-month-btn`
  }
  if (title) {
    title.id = `${props.idPrefix}-popover-title`
    title.classList.add('vc-focus')
    title.addEventListener('click', () => nextTick(makeNavAccessible))
    srAlert.innerText = title.innerText
  }
  if (weeks) {
    weeks.setAttribute('aria-labelledby', `${props.idPrefix}-popover-title`)
    weeks.role = 'grid'
  }
  each(weekdayLabels, (label, index) => {
    const abbr = document.createElement('abbr')
    abbr.innerText = label.innerText
    abbr.title = weekdays[index]
    label.innerHTML = abbr.outerHTML
  })
}

const makeNavAccessible = () => {
  const navPopover = popover.value.querySelector('.vc-nav-container')
  if (navPopover) {
    const nextYearButton = navPopover.querySelector('.vc-nav-arrow.is-right')
    const prevYearButton = navPopover.querySelector('.vc-nav-arrow.is-left')
    if (nextYearButton) {
      nextYearButton.ariaLabel = 'next year'
      nextYearButton.id = `${props.idPrefix}-popover-next-year-btn`
    }
    if (prevYearButton) {
      prevYearButton.ariaLabel = 'previous year'
      prevYearButton.id = `${props.idPrefix}-popover-prev-year-btn`
    }
  }
}

const onClickClear = (e, inputEvents) => {
  const el = document.getElementById(inputId.value)
  el.value = ''
  inputEvents.change(e)
  alertScreenReader('Cleared')
  putFocusNextTick(inputId.value)
}

const onDaykeydown = e => {
  if (e.code === 'Enter' || e.code === 'Space') {
    putFocusNextTick(`${props.idPrefix}-clear-btn`)
  }
}

const onInputKeyup = (e, inputEvents) => {
  if (e.code === 'ArrowDown') {
    let selector
    if (model.value) {
      const selectedDate = DateTime.fromJSDate(model.value).toLocaleString({...DateTime.DATE_MED, weekday: 'long'})
      selector = `[aria-label="${selectedDate}"]`
    } else {
      selector = '[tabindex="0"]'
    }
    putFocusNextTick(`${props.idPrefix}-popover`, {cssSelector: selector})
  } else {
    inputEvents.keyup(e)
  }
}

const onPopoverShown = popoverContent => {
  // Fill accessibility gaps in v-calendar date picker popover
  const helpContainer = popoverContent.querySelector('[data-helptext]')
  popoverContent.ariaLabel = `choose ${props.ariaLabel}`
  popoverContent.ariaModal = false
  popoverContent.id = `${props.idPrefix}-popover`
  popoverContent.role = 'dialog'
  if (helpContainer) {
    const helpText = helpContainer.getAttribute('data-helptext')
    const helpEl = document.createElement('span')
    helpEl.className = 'sr-only'
    helpEl.ariaLive = 'polite'
    helpEl.id = `${props.idPrefix}-popover-help`
    helpContainer.prepend(helpEl)
    setTimeout(() => {
      helpEl.innerText = helpText
    }, 200)
  }
  const liveRegion = document.createElement('span')
  liveRegion.className = 'sr-only'
  liveRegion.ariaLive = 'assertive'
  liveRegion.id = `${props.idPrefix}-popover-sr-alert`
  popoverContent.prepend(liveRegion)
  popover.value = popoverContent
  isPopoverVisible.value = true
  makeCalendarAccessible()
}

const onTransitionStart = () => {
  // When displaying a month, if maxDate falls within that month then the "next month" button
  // will be disabled (and similarly for minDate and the "previous month" button).
  // Prevent focus from landing on a disabled button and causing the popover to close prematurely.
  const prevMonthBtn = document.getElementById(`${props.idPrefix}-popover-prev-month-btn`)
  const nextMonthBtn = document.getElementById(`${props.idPrefix}-popover-next-month-btn`)
  if (prevMonthBtn.disabled) {
    nextMonthBtn.focus()
  } else if (nextMonthBtn.disabled) {
    prevMonthBtn.focus()
  }
}

const onUpdateFocus = (hasFocus, inputEvents) => {
  const el = document.getElementById(inputId.value)
  const event = {
    relatedTarget: hasFocus ? null : document.getElementById(props.containerId),
    srcElement: el,
    target: el,
    type: hasFocus ? 'focusin' : 'focusout'
  }
  hasFocus ? inputEvents.focusin(event) : inputEvents.focusout(event)
}

const onUpdateModel = (inputEvents) => {
  const el = document.getElementById(inputId.value)
  const event = {
    currentTarget: el,
    srcElement: el,
    target: el,
    type: 'input'
  }
  inputEvents.input(event)
}
</script>

<style scoped>
.date-input {
  min-width: 9.6rem;
}
</style>
