<template>
  <div>
    <h3 class="font-size-16">Topics Used</h3>
    <div v-if="noteTopics.length">
      <table class="mt-2 w-100">
        <thead class="sr-only">
          <tr>
            <th>Note Topic</th>
            <th>Note Topic Usage Count</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(noteTopic, index) in noteTopics"
            :id="`tr-note-topic-${noteTopic.id}`"
            :key="noteTopic.id"
            :class="{
              'bg-surface-light': index % 2 !== 0,
              'border-t-md': index === 0
            }"
          >
            <td :class="{'pt-2': index === 0}" class="pl-3">
              <span :id="`peer-advising-note-topic-${noteTopic.id}-title`">{{ noteTopic.topic }}</span>
            </td>
            <td class="font-weight-550 pr-3 text-right">
              <span :id="`peer-advising-note-topic-${noteTopic.id}-usage-count`">{{ numFormat(noteTopic.usageCount) }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="!noteTopics.length" class="pa-3 text-medium-emphasis">
      No peer advising topics are configured.
    </div>
  </div>
</template>

<script setup lang="ts">
import {get} from 'lodash'
import type {PropType} from 'vue'
import {numFormat} from '@/lib/utils'
import type {PeerAdvisingManagerReport} from '@/lib/types-peer-advising'

const props = defineProps({
  notesReport: {
    required: true,
    type: Object as PropType<PeerAdvisingManagerReport>
  }
})

const noteTopics = get(props.notesReport, 'noteTopics', [])
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
