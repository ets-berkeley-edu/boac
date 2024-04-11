<template>
  <div>
    <h2 class="font-size-24 font-weight-bold">Academic Timeline</h2>
    <div class="d-flex justify-space-between flex-wrap ml-2">
      <div>
        <div class="d-flex my-2">
          <div class="align-self-center sr-only">Filter Type:</div>
          <div>
            <v-btn
              id="timeline-tab-all"
              :class="{'tab-active text-white': !filter, 'tab-inactive text-dark': filter}"
              class="tab pl-2 pr-2"
              aria-controls="timeline-messages"
              :aria-selected="!filter"
              variant="text"
              @click="setFilter(null)"
            >
              All
            </v-btn>
          </div>
          <div v-for="type in _keys(filterTypes)" :key="type" role="tablist">
            <v-btn
              :id="`timeline-tab-${type}`"
              :class="{
                'tab-active text-white': type === filter && countsPerType[type],
                'tab-inactive text-dark': type !== filter && countsPerType[type],
                'tab-disabled text-grey-darken-2': !countsPerType[type]
              }"
              aria-controls="timeline-messages"
              :aria-selected="type === filter"
              :disabled="!countsPerType[type]"
              class="tab ml-2 pl-2 pr-2 text-center"
              variant="text"
              @click="setFilter(type)"
            >
              {{ filterTypes[type].tab }}
            </v-btn>
          </div>
        </div>
      </div>
      <div v-if="!currentUser.isAdmin && currentUser.canAccessAdvisingData" class="my-2">
        <v-btn
          id="new-note-button"
          :disabled="isEditingNote"
          class="mr-2 btn-primary-color-override btn-primary-color-override-opaque"
          variant="primary"
          @click="isEditingNote = true"
        >
          <span class="ma-1">
            <v-icon :icon="mdiFileOutline" />
            New Note
          </span>
        </v-btn>
      </div>
    </div>
    <EditBatchNoteModal
      v-if="isEditingNote"
      initial-mode="createNote"
      :on-close="onModalClose"
      :sid="student.sid"
    />
  </div>
</template>

<script setup>
import {mdiFileOutline} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import EditBatchNoteModal from '@/components/note/EditBatchNoteModal'
import Util from '@/mixins/Util'

export default {
  name: 'AcademicTimelineHeader',
  components: {EditBatchNoteModal},
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
    isEditingNote: false
  }),
  methods: {
    onModalClose(note) {
      this.isEditingNote = false
      this.putFocusNextTick(note && this._includes(['all', 'note'], this.activeTab) ? `timeline-tab-${this.activeTab}-message-0` : 'new-note-button')
    }
  }
}
</script>

<style scoped>
.tab {
  border-radius: 5px;
  font-size: 16px;
  font-weight: 800;
  height: 40px;
}
.tab-active {
  background-color: #555;
}
.tab-active:active,
.tab-active:focus,
.tab-active:hover {
  background-color: #444;
}
.tab-disabled {
  background-color: #ccc;
}
.tab-inactive {
  background-color: #eee;
}
.tab-inactive:hover,
.tab-inactive:hover,
.tab-inactive:hover {
  background-color: #ddd;
}
</style>
