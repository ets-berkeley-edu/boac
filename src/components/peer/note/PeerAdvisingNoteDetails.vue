<template>
  <div>
    <div v-if="!noteDetails">
      Loading...
    </div>
    <div v-if="noteDetails" :class="{'img-blur': currentUser.inDemoMode}">
      <div>
        <div v-if="noteDetails.subject" :id="`note-${noteDetails.id}-subject`">{{ noteDetails.subject }}</div>
        <div :id="`note-${noteDetails.id}-body`" v-html="noteDetails.body" />
      </div>
      <div :id="`note-${noteDetails.id}-is-open`" class="w-100" :class="{'demo-mode-blur': currentUser.inDemoMode}">
        <div v-if="noteDetails.subject && noteDetails.body" class="open-note-message-container pt-2">
          <span :id="`note-${noteDetails.id}-message-open`" v-html="noteDetails.body" />
        </div>
        <div class="mt-4">
          <div v-if="noteDetails.author.name || noteDetails.author.email">
            <span class="sr-only">Note created by </span>
            <div v-if="noteDetails.author.uid && noteDetails.author.name">
              <router-link
                v-if="currentUser.isAdmin && noteDetails.peerAdvisingDepartmentId"
                :id="`note-${noteDetails.id}-link-to-peer-advisor-home`"
                :to="`/peer_advisor/${noteDetails.author.uid}/home`"
              >
                {{ noteDetails.author.name }}
              </router-link>
              <a
                v-if="!currentUser.isAdmin || !noteDetails.peerAdvisingDepartmentId"
                :id="`note-${noteDetails.id}-author-name`"
                :aria-label="`${noteDetails.author.name} UC Berkeley Directory page (opens in new window)`"
                :href="`https://www.berkeley.edu/directory/results?search-term=${noteDetails.author.name}`"
                target="_blank"
              >
                {{ noteDetails.author.name }}
              </a>
            </div>
            <div :id="`note-${noteDetails.id}-author-role`">
              {{ capitalizeAllWords(replace(noteDetails.author.role, '_', ' ')) }}
            </div>
          </div>
          <div
            v-if="size(noteDetails.author.departments)"
            class="text-medium-emphasis"
          >
            <div v-for="(department, index) in noteDetails.author.departments" :key="index">
              <span :id="`note-${noteDetails.id}-author-dept-${index}`">{{ department.deptName }}</span>
            </div>
          </div>
          <div v-if="peerAdvisingDepartment" class="text-medium-emphasis">
            <span :id="`note-${noteDetails.id}-university-department`">{{ peerAdvisingDepartment.deptName }}</span><!--
            --><span v-if="peerAdvisingDepartment.name !== peerAdvisingDepartment.deptName" :id="`note-${noteDetails.id}-peer-advising-department`">, {{ peerAdvisingDepartment.name }}</span>
          </div>
        </div>
        <div v-if="noteDetails.topics && size(noteDetails.topics)" class="mt-3">
          <AdvisingNoteTopics :note="noteDetails" read-only />
        </div>
        <div v-if="noteDetails.contactType" class="mt-3">
          <div class="font-size-16 font-weight-bold text-medium-emphasis">Contact Type</div>
          <div :id="`note-${noteDetails.id}-contact-type`">{{ noteDetails.contactType }}</div>
        </div>
      </div>
      <AdvisingNoteAttachments
        v-if="size(noteDetails.attachments)"
        :attachments="noteDetails.attachments"
        class="attachments-edit mt-3"
        :disabled="false"
        :id-prefix="`note-${noteDetails.id}-`"
        :is-downloadable="true"
        :is-read-only="true"
        :note="noteDetails"
      />
      <div v-if="showCreatedAt" :id="`note-${note.id}-created-at`" class="mt-2 text-medium-emphasis">
        Date created: {{ DateTime.fromISO(noteDetails.createdAt).toLocaleString(DateTime.DATE_MED) }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {DateTime} from 'luxon'
import {onMounted, ref} from 'vue'
import {replace, size} from 'lodash'
import type {Note, PeerAdvisingDepartment} from '@/lib/types'
import AdvisingNoteAttachments from '@/components/note/AdvisingNoteAttachments.vue'
import AdvisingNoteTopics from '@/components/note/AdvisingNoteTopics.vue'
import {capitalizeAllWords} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {getPeerAdvisorNoteById} from '@/api/peer-advising-notes'
import {findPeerAdvisingDepartment} from '@/lib/berkeley-department'

const props = defineProps({
  note: {
    required: false,
    type: Object as PropType<Note>,
    default: undefined
  },
  noteId: {
    required: false,
    type: Number,
    default: undefined
  },
  showCreatedAt: {
    required: false,
    type: Boolean
  }
})

const currentUser = useContextStore().currentUser
const noteDetails = ref()
const noteLoaded = ref(false)
const peerAdvisingDepartment = ref<PeerAdvisingDepartment>()

onMounted(() => {
  const setNoteDetails = data => {
    noteDetails.value = data
    peerAdvisingDepartment.value = findPeerAdvisingDepartment(noteDetails.value.peerAdvisingDepartmentId)
    noteLoaded.value = true
  }
  if (!props.note && props.noteId) {
    getPeerAdvisorNoteById(props.noteId).then(setNoteDetails)
  } else {
    setNoteDetails(props.note)
  }
})
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
