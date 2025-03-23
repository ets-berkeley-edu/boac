<template>
  <div class="ma-3">
    <h2 class="font-size-18">Reporting &amp; Statistics</h2>
    <div v-if="notesReport" class="d-flex justify-space-between mt-3">
      <div class="w-50 pr-4">
        <table class="w-100">
          <thead class="sr-only">
            <tr>
              <th>Measurement</th>
              <th>Value</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Total {{ peerAdvisingDepartment.name }} peer advising notes</td>
              <td class="text-right">{{ notesReport.totalPeerAdvisingNoteCount }}</td>
            </tr>
            <tr>
              <td>Distinct peer advisor authors</td>
              <td class="text-right">{{ notesReport.distinctPeerAdvisorAuthors }}</td>
            </tr>
          </tbody>
        </table>
        <h3 class="font-size-16 mt-3">Templates Used</h3>
        <div class="ml-3">
          <table class="w-100">
            <thead class="sr-only">
              <tr>
                <th>Measurement</th>
                <th>Value</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="noteTemplate in notesReport.noteTemplates" :key="noteTemplate.name">
                <td>{{ noteTemplate.name }}</td>
                <td class="text-right">{{ noteTemplate.usageCount }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="pl-4 w-50">
        XXX
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {onMounted, ref} from 'vue'
import {getPeerAdvisingNotesReport} from '@/api/peer-advising-reports'
import type {PeerAdvisingDepartment} from '@/lib/types'

const props = defineProps({
  peerAdvisingDepartment: {
    required: true,
    type: Object as PropType<PeerAdvisingDepartment>
  }
})

const notesReport = ref(undefined)

onMounted(() => {
  getPeerAdvisingNotesReport(props.peerAdvisingDepartment.id).then(data => {
    notesReport.value = data
  })
})
</script>

<style scoped>

</style>
