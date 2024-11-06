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
      <div
        class="custom-text-field"
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
          class="date-input"
          :disabled="disabled"
          :value="inputValue"
          placeholder="MM/DD/YYYY"
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
        />
        <button
          v-if="inputValue && !disabled"
          :id="`${idPrefix}-clear-btn`"
          :aria-label="`Clear ${ariaLabel}`"
          class="clear-button clear-icon"
          @click.stop.prevent="onClickClear($event, inputEvents)"
        >
          <v-icon :icon="mdiCloseCircleOutline"></v-icon>
        </button>
      </div>
    </template>
  </date-picker>
</template>


<script setup>
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {computed, nextTick, onBeforeUnmount, onMounted, ref} from 'vue'
import {DateTime} from 'luxon'
import {each} from 'lodash'
import {mdiCloseCircleOutline} from '@mdi/js'

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

onBeforeUnmount(() => {
  const container = document.getElementById(props.containerId)
  if (container) {
    container.removeEventListener('keydown', onKeydownPreventClick)
  }
})

onMounted(() => {
  // Setting this as a prop on the VTextField component breaks the "clear" button.
  document.getElementById(inputId.value).setAttribute('role', 'combobox')
  // Workaround for https://github.com/nathanreyes/v-calendar/issues/1459
  document.getElementById(props.containerId).addEventListener('keydown', onKeydownPreventClick)
})

const isMonthNavBtn = el => el.id === `${props.idPrefix}-popover-next-month-btn` || el.id === `${props.idPrefix}-popover-prev-month-btn`

const isSpaceOrEnter = key => {
  return key === ' ' || key === 'Spacebar' || key === 'Enter'
}
const onKeydownPreventClick = e => {
  if (e && isMonthNavBtn(e.target) && isSpaceOrEnter(e.key)) {
    e.preventDefault()
  }
}

const isValid = dateString => {
  if (!dateString || dateString === '') {
    return true
  }
  const date = DateTime.fromFormat(dateString, 'MM/dd/yyyy')
  return date.isValid
}

const makeCalendarAccessible = () => {
  if (!popover.value) return

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
  const inputElement = document.getElementById(inputId.value)
  if (inputElement) {
    inputElement.value = ''
    inputEvents.change(e)
    alertScreenReader('Cleared')
    putFocusNextTick(inputId.value)
    model.value = null
  }
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

  if (prevMonthBtn && prevMonthBtn.disabled) {
    nextMonthBtn?.focus()
  } else if (nextMonthBtn && nextMonthBtn.disabled) {
    prevMonthBtn?.focus()
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

const onInput = (event, inputEvents) => {
  inputEvents.input(event)
}
</script>


<style scoped>
.custom-text-field {
  position: relative;
  display: flex;
  align-items: center;
  border: 1px solid #ccc; /* Border color similar to v-text-field */
  border-radius: 4px;
  padding: 0 12px;
  background-color: white;
  transition: border-color 0.3s;
}

.custom-text-field input {
  flex: 1;
  border: none;
  outline: none;
  padding: 8px 0;
  font-size: 16px;
  background-color: transparent;
}

.custom-text-field input::placeholder {
  color: #aaa;
}

.custom-text-field .clear-button {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.custom-text-field .clear-icon {
  width: 20px;
  height: 20px;
  color: #999; /* Icon color */
}

.custom-text-field.error--text {
  border-color: red;
}

.custom-text-field.disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.custom-text-field.disabled input {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.custom-text-field:hover {
  border-color: #aaa;
}

.custom-text-field:focus-within {
  border-color: #1976d2; /* Primary color on focus */
}
</style>

