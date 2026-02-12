<template>
  <div
    :id="`${idPrefix}-counter`"
    ref="counter"
    class="font-size-14 text-no-wrap text-right"
  >
    <span v-if="count" :class="{'text-error': count === max}">
      {{ pluralize('character', max - count) }} left
    </span>
    <span v-if="!count">
      {{ max }} characters allowed
    </span>
  </div>
</template>

<script setup lang="ts">
import {first} from 'lodash'
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
@media (max-width: 600px) {
  .v-input__details .v-counter {
    width: 100%;
  }
}
</style>
