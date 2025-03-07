<template>
  <div>
    <div>
      <div v-if="note.subject" :id="`note-${note.id}-subject`">{{ note.subject }}</div>
      <div :id="`note-${note.id}-body`" v-html="note.body" />
    </div>
    <div :id="`note-${note.id}-is-open`" class="w-100">
      <div v-if="note.subject && note.body" class="open-note-message-container pt-2">
        <span :id="`note-${note.id}-message-open`" v-html="note.body" />
      </div>
      <div class="mt-3">
        <div v-if="note.author.name || note.author.email">
          <span class="sr-only">Note created by </span>
          <span v-if="note.author.uid && note.author.name">
            <router-link
              v-if="currentUser.isAdmin && note.peerAdvisingDepartmentId"
              :id="`note-${note.id}-link-to-peer-advisor-home`"
              :to="`/peer_advisor/${note.author.uid}/home`"
            >
              {{ note.author.name }}
            </router-link>
            <a
              v-if="!currentUser.isAdmin || !note.peerAdvisingDepartmentId"
              :id="`note-${note.id}-author-name`"
              :aria-label="`${note.author.name} UC Berkeley Directory page (opens in new window)`"
              :href="`https://www.berkeley.edu/directory/results?search-term=${note.author.name}`"
              target="_blank"
            >
              {{ note.author.name }}
            </a>
          </span>
          <span v-if="note.author.role">- <span :id="`note-${note.id}-author-role`">{{ capitalizeAllWords(replace(note.author.role, '_', ' ')) }}</span></span>
        </div>
        <div v-if="size(note.author.departments)" class="text-medium-emphasis">
          <div v-for="(department, index) in note.author.departments" :key="index">
            <span :id="`note-${note.id}-author-dept-${index}`">{{ department.deptName }}</span>
          </div>
        </div>
      </div>
      <div v-if="note.topics && size(note.topics)" class="py-2">
        <AdvisingNoteTopics :note="note" read-only />
      </div>
      <div v-if="note.contactType" class="py-2">
        <div class="font-weight-bold">Contact Type</div>
        <div :id="`note-${note.id}-contact-type`">{{ note.contactType }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {replace, size} from 'lodash'
import type {Note} from '@/lib/types'
import AdvisingNoteTopics from '@/components/note/AdvisingNoteTopics.vue'
import {capitalizeAllWords} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

defineProps({
  note: {
    required: true,
    type: Object as PropType<Note>
  }
})

const currentUser = useContextStore().currentUser
</script>

<style>
.open-note-message-container ul {
  margin: 0 30px 0 30px;
}
</style>

<style scoped>
.open-note-message-container {
  overflow-wrap: break-word;
}
</style>
