<template>
  <div
    :id="`${idPrefix}-counter`"
    ref="counter"
    :aria-live="count ? 'polite' : 'off'"
    class="font-size-14 text-no-wrap text-right"
    :role="count ? 'status' : 'none'"
  >
    <div
      v-if="!isUndefined(max)"
      :class="{'text-error': count === max}"
    >
      <span v-if="!count">
        {{ max }} characters allowed
      </span>
      <span v-if="count">{{ pluralize('character', max - count) }} left</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import {first, isUndefined} from 'lodash'
import {onMounted, ref} from 'vue'
import {pluralize} from '@/lib/utils'

defineProps({
  count: {
    required: true,
    type: Number
  },
  idPrefix: {
    default: 'character',
    required: false,
    type: String
  },
  max: {
    required: true,
    type: Number
  }
})

const counter = ref()

onMounted(() => {
  const detailsEl = counter.value.closest('.v-input__details')
  const id = detailsEl.getAttribute('id')
  const messagesEl: Element = first(detailsEl.children)
  detailsEl.setAttribute('role', 'none')
  detailsEl.setAttribute('aria-live', 'off')
  detailsEl.setAttribute('id', id.replace('messages', 'details'))
  messagesEl.setAttribute('id', id)
})
</script>

<style>
.v-input__details {
  flex-wrap: wrap-reverse;
  justify-content: end;
  padding-inline: 0px !important;
  .v-messages {
    min-width: 18.75rem;
    width: 70%;
    .v-messages__message {
      word-break: auto-phrase;
    }
  }
  .v-counter {
    min-width: 12rem;
    padding-inline: 16px;
    width: 30%;
  }
}
</style>
