<template>
  <div>
    <h3 class="font-size-16">Templates Used</h3>
    <div v-if="noteTemplates.length">
      <table class="mt-2 w-100">
        <thead class="sr-only">
          <tr>
            <th>Note Template Title</th>
            <th>Note Template Usage Count</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(noteTemplate, index) in noteTemplates"
            :id="`tr-note-template=${noteTemplate.id}`"
            :key="noteTemplate.id"
            :class="{
              'bg-surface-light': index % 2 !== 0,
              'border-t-md': index === 0
            }"
          >
            <td :class="{'pt-2': index === 0}" class="pl-3">
              <span :id="`peer-advising-note-template-${noteTemplate.id}-title`">{{ noteTemplate.templateTitle }}</span>
            </td>
            <td class="font-weight-550 pr-3 text-right">
              <span :id="`peer-advising-note-template-${noteTemplate.id}-usage-count`">{{ noteTemplate.noteTemplateUsageCount }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="!noteTemplates.length" class="pa-3 text-medium-emphasis">
      {{ notesReport.peerAdvisingDepartment.name }} has no note templates.
    </div>
  </div>
</template>

<script setup lang="ts">
import {get} from 'lodash'
import type {PropType} from 'vue'
import type {PeerAdvisingManagerReport} from '@/lib/types-peer-advising'

const props = defineProps({
  notesReport: {
    required: true,
    type: Object as PropType<PeerAdvisingManagerReport>
  }
})

const noteTemplates = get(props.notesReport, 'noteTemplates', [])
</script>

<style scoped>
table {
  border-collapse: collapse;
}
td {
  padding: 4px 0 4px 0;
}
td:first-child {
  padding-left: 8px;
}
</style>
