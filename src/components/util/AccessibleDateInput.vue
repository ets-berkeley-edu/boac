<template>
  <date-picker
    v-model.date="model"
    :input-debounce="500"
    :max-date="maxDate"
    :popover="{placement: 'top', visibility: 'focus'}"
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
            :id="`${inputId}-clear-btn`"
            aria-label="Clear date"
            class="d-flex align-self-center"
            density="compact"
            :disabled="disabled"
            :icon="mdiCloseCircle"
            size="20px"
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
  inputId: {
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

const isValid = dateString => {
  if (!dateString || dateString === '') {
    return true
  }
  const date = DateTime.fromFormat(dateString, 'MM/dd/yyyy')
  return date.isValid
}

const onClickClear = (inputEvents) => {
  const el = document.getElementById(props.inputId)
  el.value = ''
  const event = {
    currentTarget: el,
    srcElement: el,
    target: el,
    type: 'change'
  }
  inputEvents.change(event)
  alertScreenReader('Cleared')
  putFocusNextTick(props.inputId)
}

const onPopoverShown = popoverContent => {
  // Fill accessibility gaps in v-calendar date picker popover
  const helpContainer = popoverContent.querySelector('[data-helptext]')
  const nextMonthBtn = popoverContent.querySelector('.is-right')
  const prevMonthBtn = popoverContent.querySelector('.is-left')
  const title = popoverContent.querySelector('.vc-title')
  const weeks = popoverContent.querySelector('.vc-weeks')
  const weekdayLabels = popoverContent.querySelectorAll('.vc-weekday')
  const weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  popoverContent.ariaLabel = 'choose date'
  popoverContent.ariaModal = false
  popoverContent.role = 'dialog'
  if (helpContainer) {
    const helpText = helpContainer.getAttribute('data-helptext')
    const helpEl = document.createElement('span')
    helpEl.className = 'sr-only'
    helpEl.ariaLive = 'polite'
    helpContainer.prepend(helpEl)
    setTimeout(() => {
      helpEl.innerText = helpText
    }, 200)
  }
  if (nextMonthBtn) {
    nextMonthBtn.ariaLabel = 'previous month'
  }
  if (prevMonthBtn) {
    prevMonthBtn.ariaLabel = 'previous month'
  }
  if (title) {
    title.ariaLive = 'polite'
    title.id = `${props.inputId}-popover-title`
    title.classList.add('vc-focus')
  }
  if (weeks) {
    weeks.setAttribute('aria-labelledby', `${props.inputId}-popover-title`)
    weeks.role = 'grid'
  }
  each(weekdayLabels, (label, index) => {
    label.abbr = weekdays[index]
  })
}

const onUpdateFocus = (hasFocus, inputEvents) => {
  const el = document.getElementById(props.inputId)
  const event = {
    relatedTarget: hasFocus ? null : document.getElementById(props.containerId),
    srcElement: el,
    target: el,
    type: hasFocus ? 'focusin' : 'focusout'
  }
  hasFocus ? inputEvents.focusin(event) : inputEvents.focusout(event)
}

const onUpdateModel = (v, inputEvents) => {
  const el = document.getElementById(props.inputId)
  const event = {
    currentTarget: el,
    srcElement: el,
    target: el,
    type: 'input'
  }
  inputEvents.input(event)
}

</script>
