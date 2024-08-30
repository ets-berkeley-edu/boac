<template>
  <date-picker
    v-model.date="model"
    :input-debounce="500"
    :max-date="maxDate"
    :popover="{placement: 'top', visibility: 'focus'}"
    @did-move="makeCalendarAccessible"
    @popover-did-show="onPopoverShown"
  >
    <template #default="{ inputValue, inputEvents }">
      <v-text-field
        :id="inputId"
        :aria-describedby="ariaDescribedby"
        clearable
        :error="!isValid(inputValue)"
        hide-details
        :model-value="inputValue"
        persistent-clear
        placeholder="MM/DD/YYYY"
        validate-on="blur"
        @click:clear="onClickClear(inputEvents)"
        @keyup="inputEvents.keyup"
        @mouseleave="inputEvents.mouseleave"
        @mousemove="inputEvents.mousemove"
        @update:focused="hasFocus => onUpdateFocus(hasFocus, inputEvents)"
        @update:model-value="v => onUpdateModel(v, inputEvents)"
      >
        <template #clear>
          <v-btn
            :id="`${idPrefix}-clear-btn`"
            aria-label="Clear date"
            class="d-flex align-self-center"
            density="compact"
            :disabled="disabled"
            exact
            :icon="mdiCloseCircle"
            variant="text"
            @click.stop.prevent="onClickClear(inputEvents)"
          />
        </template>
      </v-text-field>
    </template>
  </date-picker>
</template>

<script setup>
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {computed, ref} from 'vue'
import {DateTime} from 'luxon'
import {each} from 'lodash'
import {mdiCloseCircle} from '@mdi/js'

const props = defineProps({
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
const popover = ref()

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
  const title = popover.value.querySelector('.vc-title')
  const weeks = popover.value.querySelector('.vc-weeks')
  const weekdayLabels = popover.value.querySelectorAll('.vc-weekday')
  if (nextMonthBtn) {
    nextMonthBtn.ariaLabel = 'previous month'
    nextMonthBtn.id = `${props.idPrefix}-popover-next-btn`
  }
  if (prevMonthBtn) {
    prevMonthBtn.ariaLabel = 'previous month'
    prevMonthBtn.id = `${props.idPrefix}-popover-prev-btn`
  }
  if (title) {
    title.ariaLive = 'polite'
    title.id = `${props.idPrefix}-popover-title`
    title.classList.add('vc-focus')
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
  alertScreenReader(title.innerText)
}

const onClickClear = (inputEvents) => {
  const el = document.getElementById(inputId.value)
  el.value = ''
  const event = {
    currentTarget: el,
    srcElement: el,
    target: el,
    type: 'change'
  }
  inputEvents.change(event)
  alertScreenReader('Cleared')
  putFocusNextTick(inputId.value)
}

const onPopoverShown = popoverContent => {
  // Fill accessibility gaps in v-calendar date picker popover
  const helpContainer = popoverContent.querySelector('[data-helptext]')
  popoverContent.ariaLabel = 'choose date'
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
  popover.value = popoverContent
  makeCalendarAccessible()
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

const onUpdateModel = (v, inputEvents) => {
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
