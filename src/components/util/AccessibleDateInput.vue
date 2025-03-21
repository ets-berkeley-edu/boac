<template>
  <div class="accessible-date-picker d-flex position-relative">
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
      @daykeydown="(day, e) => onKeyDownDay(e)"
      @popover-did-hide="() => isPopoverVisible = false"
      @popover-did-show="onPopoverShown"
      @transition-start="() => onTransitionStart"
    >
      <template #default="{ inputValue, inputEvents }">
        <div
          class="custom-text-field w-100"
          :class="{ 'error--text': !isValid(inputValue), disabled: disabled }"
          :aria-invalid="!isValid(inputValue)"
        >
          <input
            :id="inputId"
            type="text"
            :aria-controls="`${idPrefix}-popover`"
            :aria-describedby="ariaDescribedby"
            :aria-expanded="isPopoverVisible"
            aria-haspopup="dialog"
            :aria-required="required"
            autocomplete="off"
            :disabled="disabled"
            maxlength="10"
            placeholder="MM/DD/YYYY"
            :value="inputValue"
            @input="onInput($event, inputEvents)"
            @keyup="onInputKeyup($event, inputEvents)"
            @mouseleave="inputEvents.mouseleave"
            @mousemove="inputEvents.mousemove"
            @focus="() => onUpdateFocus(true, inputEvents)"
            @blur="() => onUpdateFocus(false, inputEvents)"
            @keydown="inputEvents.keydown"
            @paste="inputEvents.paste"
            @select="inputEvents.select"
            @change="inputEvents.change"
            @focusin="inputEvents.focusin"
            @focusout="inputEvents.focusout"
          >
        </div>
      </template>
    </date-picker>
    <button
      v-if="model"
      :id="`${idPrefix}-clear-btn`"
      :aria-label="`Clear ${ariaLabel}`"
      class="clear-button clear-icon mb-1"
      :disabled="disabled"
      @click.stop.prevent="onClickClear($event, dateInputEvents)"
    >
      <v-icon
        color="secondary"
        height="20"
        :icon="mdiCloseCircle"
        width="20"
      />
    </button>
  </div>
</template>

<script setup>
import {DateTime} from 'luxon'
import {each} from 'lodash'
import {mdiCloseCircle} from '@mdi/js'
import {nextTick, onBeforeUnmount, onMounted, ref} from 'vue'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'

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
const dateInputEvents = ref(undefined)
const inputId = `${props.idPrefix}-input`
const isPopoverVisible = ref(false)
const popover = ref()

onBeforeUnmount(() => {
  const container = document.getElementById(props.containerId)
  if (container) {
    container.removeEventListener('keydown', onKeyDownPreventClick)
  }
})

onMounted(() => {
  // Setting this as a prop on the VTextField component breaks the "clear" button.
  document.getElementById(inputId).setAttribute('role', 'combobox')
  // Workaround for https://github.com/nathanreyes/v-calendar/issues/1459
  document.getElementById(props.containerId).addEventListener('keydown', onKeyDownPreventClick)
})

const isMonthNavBtn = el => el.id === `${props.idPrefix}-popover-next-month-btn` || el.id === `${props.idPrefix}-popover-prev-month-btn`

const isSpaceOrEnter = key => {
  return key === ' ' || key === 'Spacebar' || key === 'Enter'
}

const isValid = dateString => {
  if (!dateString || dateString === '') {
    return true
  }
  const date = DateTime.fromFormat(dateString, 'MM/dd/yyyy')
  return date.isValid
}

const makeCalendarAccessible = () => {
  if (popover.value) {
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
}

const makeNavAccessible = () => {
  const navPopover = popover.value ? popover.value.querySelector('.vc-nav-container') : null
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
  const inputElement = document.getElementById(inputId)
  if (inputElement) {
    inputElement.value = ''
    inputEvents.change(e)
    alertScreenReader('Cleared')
    putFocusNextTick(inputId)
    model.value = null
  }
}

const onInput = (event, inputEvents) => inputEvents.input(event)

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

const onKeyDownDay = e => {
  if (e.code === 'Enter' || e.code === 'Space') {
    putFocusNextTick(`${props.idPrefix}-clear-btn`)
  }
}

const onKeyDownPreventClick = e => {
  if (e && isMonthNavBtn(e.target) && isSpaceOrEnter(e.key)) {
    e.preventDefault()
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

  if (prevMonthBtn && prevMonthBtn.disabled) {
    nextMonthBtn?.focus()
  } else if (nextMonthBtn && nextMonthBtn.disabled) {
    prevMonthBtn?.focus()
  }
}

const onUpdateFocus = (hasFocus, inputEvents) => {
  const el = document.getElementById(inputId)
  const event = {
    relatedTarget: hasFocus ? null : document.getElementById(props.containerId),
    srcElement: el,
    target: el,
    type: hasFocus ? 'focusin' : 'focusout'
  }
  dateInputEvents.value = inputEvents
  if (hasFocus) {
    inputEvents.focusin(event)
  } else inputEvents.focusout(event)
}
</script>

<style scoped>
.accessible-date-picker {
  width: 150px;
}
.clear-button {
  background: transparent;
  border: none;
  border-radius: 100%;
  cursor: pointer;
  padding: 2px 4px 2px 2px;
  position: absolute;
  right: 5px;
  top: 5px;
  &:disabled {
    cursor: not-allowed;
    opacity: var(--v-disabled-opacity);
  }
}
.custom-text-field {
  --v-field-border-opacity: 0.38;
  --v-field-border-width: 1px;
  --v-field-border-color: var(--v-theme-primary);
  align-items: center;
  background-color: white;
  border: var(--v-field-border-width) solid rgba(var(--v-field-border-color), var(--v-field-border-opacity));
  border-radius: 4px;
  display: flex;
  height: 40px;
  padding: .375rem .75rem;
  transition: border-color 0.3s;
  &:focus-within {
    --v-field-border-opacity: 1;
    --v-field-border-width: 1.875px;
    border-color: rgb(var(--v-theme-on-surface));
    outline: 0;
  }
  &:hover:not(.disabled) {
    --v-field-border-opacity: var(--v-high-emphasis-opacity);
  }
}
.custom-text-field input {
  background-color: transparent;
  border: none;
  flex: 1;
  font-size: 16px;
  line-height: 1.5;
  outline: none;
  padding: 8px 0;
  &:disabled {
    cursor: not-allowed;
    opacity: var(--v-disabled-opacity);
  }
}
.custom-text-field input::placeholder {
  color: rgba(var(--v-theme-on-surface), var(--v-medium-emphasis-opacity));
}
.custom-text-field.error--text {
  border-color: rgb(var(--v-theme-error));
}
</style>

