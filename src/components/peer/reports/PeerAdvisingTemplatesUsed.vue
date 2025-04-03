<template>
  <h3 class="font-size-16">Templates Used</h3>
  <table class="ml-3 w-100">
    <thead class="sr-only">
      <tr>
        <th>Note Template Title</th>
        <th>Note Template Usage Count</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(noteTemplate, index) in get(notesReport, 'noteTemplates', [])" :key="noteTemplate.name">
        <td :class="{'pt-2': index === 0}">{{ noteTemplate.templateTitle }}</td>
        <td class="font-weight-bold text-right">{{ noteTemplate.noteTemplateUsageCount }}</td>
      </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts">
import {get} from 'lodash'
import type {PropType} from 'vue'
import type {PeerAdvisingManagerReport} from '@/lib/types-peer-advising'

defineProps({
  notesReport: {
    required: true,
    type: Object as PropType<PeerAdvisingManagerReport | undefined>
  }
})
</script>

<style scoped>
td {
  padding: 4px 0 4px 0;
}
td:first-child {
  padding-left: 8px;
}
</style>
