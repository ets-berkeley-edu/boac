<template>
  <div class="align-end d-flex flex-wrap justify-space-between py-1 w-100">
    <div>
      <h2 class="font-size-24 font-weight-bold py-0 text-primary">Academic Timeline</h2>
    </div>
    <div v-if="!currentUser.isAdmin && currentUser.canAccessAdvisingData" class="mt-1">
      <v-btn
        id="new-note-button"
        class="border-e-sm"
        color="primary"
        :disabled="isEditingNote"
        :prepend-icon="mdiFileDocument"
        size="large"
        text="New Note"
        @click="isEditingNote = true"
      />
      <EditBatchNoteModal
        v-if="isEditingNote"
        initial-mode="createNote"
        is-open="isEditingNote"
        :on-close="onModalClose"
        :sid="student.sid"
      />
    </div>
  </div>
  <div class="border-b-sm d-flex flex-wrap justify-space-between w-100">
    <div>
      <v-tabs
        v-model="selectedTab"
        class="mt-2"
        color="primary"
        density="compact"
        :direction="$vuetify.display.mdAndUp ? 'horizontal' : 'vertical'"
        selected-class="bg-sky-blue font-weight-bold"
        @update:model-value="onUpdateTabsModel"
      >
        <v-tab id="timeline-tab-all" class="border-s-sm border-t-sm" value="all">
          <span class="sr-only">Show </span>All
        </v-tab>
        <v-tab
          v-for="(type, index) in _keys(filterTypes)"
          :id="`timeline-tab-${type}`"
          :key="type"
          :class="{
            'border-s-sm border-t-sm': countsPerType[type],
            'border-s-md border-t-md': !countsPerType[type],
            'border-e-sm': index + 1 === _keys(filterTypes).length
          }"
          :disabled="!countsPerType[type]"
          :value="type"
        >
          <span class="sr-only">Show </span>{{ filterTypes[type].tab }}
        </v-tab>
      </v-tabs>
    </div>
  </div>
</template>

<script setup>
import EditBatchNoteModal from '@/components/note/EditBatchNoteModal'
import {mdiFileDocument} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'

export default {
  name: 'AcademicTimelineHeader',
  mixins: [Context, Util],
  props: {
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
  },
  data: () => ({
    isEditingNote: false,
    selectedTab: undefined
  }),
  methods: {
    onModalClose(note) {
      this.isEditingNote = false
      this.putFocusNextTick(note && this._includes(['all', 'note'], this.activeTab) ? `timeline-tab-${this.activeTab}-message-0` : 'new-note-button')
    },
    onUpdateTabsModel(value) {
      this.setFilter(value === 'all' ? null : value)
    }
  }
}
</script>
