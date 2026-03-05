<template>
  <h2 :id="`${resultsType}-results-page-header`" class="font-size-18 font-weight-regular mr-2 py-1">
    <span v-if="countTotal">
      <span v-if="countTotal <= countInView">
        Showing {{ pluralize(resultsType, countTotal, {1: 'one'}) }}
        <span v-if="searchPhrase">
          matching <strong class="font-weight-600">{{ searchPhrase }}</strong>.
        </span>
      </span>
      <span v-if="countTotal > countInView" class="font-size-18">
        Showing {{ resultsType }}s
        <span aria-hidden="true"> 1-{{ countInView }}</span>
        <span class="sr-only"> 1 to {{ countInView }}</span>
        of {{ toInt(countTotal, 0).toLocaleString() }}
        <span v-if="searchPhrase">
          matching <strong class="font-weight-600">{{ searchPhrase }}</strong>.
        </span>
      </span>
    </span>
    <span v-if="!countTotal">
      Showing {{ countInView }} {{ resultsType }}s
      <span v-if="searchPhrase">
        matching <strong class="font-weight-600">{{ searchPhrase }}</strong>.
      </span>
    </span>
    <span v-if="!countTotal || countTotal > countInView">
      Refine your search if you have too many results.
    </span>
  </h2>
</template>

<script setup>
import {pluralize, toInt} from '@/lib/utils'

defineProps({
  countInView: {
    required: true,
    type: [Number, String]
  },
  countTotal: {
    required: true,
    type: Number
  },
  resultsType: {
    required: true,
    type: String
  },
  searchPhrase: {
    default: undefined,
    required: false,
    type: String
  }
})
</script>
