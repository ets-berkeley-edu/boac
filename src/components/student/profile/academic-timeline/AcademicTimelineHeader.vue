<template>
  <div>
    <div class="align-start d-flex flex-wrap justify-space-between pb-1 w-100">
      <div>
        <h2 id="student-academic-timeline-header" class="font-size-24 font-weight-bold py-0">Academic Timeline</h2>
      </div>
      <div v-if="!currentUser.isAdmin && currentUser.canAccessAdvisingData">
        <v-btn
          id="new-note-button"
          :aria-label="`New Note for ${student.name}`"
          class="border-e-sm mb-1"
          color="primary"
          :disabled="!!noteStore.mode"
          :prepend-icon="mdiFileDocument"
          text="New Note"
          @click="() => isEditingNote = true"
        />
        <EditBatchNoteModal
          v-model="isEditingNote"
          initial-mode="createNote"
          :on-close="onModalClose"
          :sid="student.sid"
        />
      </div>
    </div>
    <v-tabs
      v-if="!isAcademicTimelineEmpty"
      v-model="selectedTab"
      class="timeline-tabs"
      aria-label="Academic Timeline"
      :aria-orientation="$vuetify.display.mdAndUp ? 'horizontal' : 'vertical'"
      :class="{'horizontal-tabs': $vuetify.display.mdAndUp}"
      color="primary"
      density="compact"
      :direction="$vuetify.display.mdAndUp ? 'horizontal' : 'vertical'"
      selected-class="bg-sky-blue font-weight-bold"
      @update:model-value="onUpdateTabsModel"
    >
      <v-tab
        v-if="tabs.length > 1"
        id="timeline-tab-all"
        aria-controls="timeline-messages"
        :class="{
          'bg-white border-b-0': selectedTab === 'all',
          'bg-grey-lighten-4 border-b-md': selectedTab !== 'all'
        }"
        class="border-s-sm border-e-sm border-t-sm pb-1 rounded-t-lg"
        value="all"
        variant="text"
      >
        <span class="sr-only">Show </span>All <span class="letter-spacing-compact ml-1">({{ countsPerType['all'] }})</span>
      </v-tab>
      <!-- eslint-disable-next-line vue/no-v-for-template-key -->
      <template v-for="(tab, index) in tabs" :key="tab">
        <v-tab
          :id="`timeline-tab-${tab}`"
          class="border-s-sm border-e-sm border-t-sm pb-1 rounded-t-lg"
          :class="{
            'bg-white border-b-0': selectedTab === tab,
            'bg-grey-lighten-4 border-b-md': selectedTab !== tab,
            'ml-0': index === 0
          }"
          :value="tab"
          variant="text"
        >
          <span class="sr-only">Show </span>{{ filterTypes[tab].tab }} <span class="letter-spacing-compact ml-1">({{ countsPerType[tab] }})</span>
        </v-tab>
      </template>
    </v-tabs>
  </div>
</template>

<script setup>
import {filter as _filter, includes, keys} from 'lodash'
import {mdiFileDocument} from '@mdi/js'
import {computed, ref} from 'vue'
import {putFocusNextTick} from '@/lib/utils'
import EditBatchNoteModal from '@/components/note/EditBatchNoteModal'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

const props = defineProps({
  countsPerType: {
    required: true,
    type: Object
  },
  filter: {
    default: undefined,
    required: false,
    type: String
  },
  filterTypes: {
    required: true,
    type: Object
  },
  setFilter: {
    required: true,
    type: Function
  },
  student: {
    required: true,
    type: Object
  }
})

const contextStore = useContextStore()
const noteStore = useNoteStore()

const currentUser = contextStore.currentUser
const isAcademicTimelineEmpty = !props.countsPerType['all']
const isEditingNote = ref(false)
const selectedTab = ref(undefined)
const tabs = computed(() => _filter(keys(props.filterTypes), key => !!props.countsPerType[key]))

const onModalClose = note => {
  isEditingNote.value = false
  putFocusNextTick(note && includes(['all', 'note'], selectedTab) ? `timeline-tab-${selectedTab.value}-message-0` : 'new-note-button')
}

const onUpdateTabsModel = value => props.setFilter(value === 'all' ? null : value)
</script>

<style scoped>
.horizontal-tabs {
  min-width: 680px;
}
.timeline-tabs :deep(.v-slide-group__content) {
  gap: 8px;
}
</style>
