<template>
  <h2 :id="`${resultsType}-results-page-header`" class="font-size-18 font-weight-regular mr-2">
    <span v-if="countTotal">
      <span v-if="countTotal <= countInView">
        Showing {{ pluralize(resultsType, countTotal, {1: 'one'}) }}<span v-if="searchPhrase"> matching <span class="font-weight-500">{{ searchPhrase }}</span></span>.
      </span>
      <span v-if="countTotal > countInView" class="font-size-18">
        Showing {{ resultsType }}s 1-{{ countInView }} of {{ countTotal }}<span v-if="searchPhrase"> matching <span class="font-weight-500">{{ searchPhrase }}</span></span>.
      </span>
    </span>
    <span v-if="!countTotal">
      Showing {{ countInView }} {{ resultsType }}s<span v-if="searchPhrase"> matching <span class="font-weight-500">{{ searchPhrase }}</span></span>.
    </span>
  </h2>
</template>

<script setup>
import {pluralize} from '@/lib/utils'

defineProps({
  countInView: {
    required: true,
    type: [Number, String]
  },
  countTotal: {
    default: undefined,
    required: false,
    type: Number
  },
  resultsType: {
    required: true,
    type: String
  },
  searchPhrase: {
    required: true,
    type: String
  }
})
</script>
