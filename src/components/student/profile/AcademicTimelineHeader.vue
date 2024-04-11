<template>
  <div class="mb-1">
    <h2 class="font-size-24 font-weight-bold">Academic Timeline</h2>
  </div>
  <div class="d-flex flex-wrap w-100">
    <v-btn-toggle
      class="border-md font-weight-bold"
      color="primary"
      divided
      rounded="lg"
    >
      <v-btn
        id="timeline-tab-all"
        :ripple="false"
        @click="setFilter(null)"
      >
        <span class="sr-only">Show </span>All
      </v-btn>
      <v-btn
        v-for="type in _keys(filterTypes)"
        :id="`timeline-tab-${type}`"
        :key="type"
        :class="{'border-surface border-s-sm': !countsPerType[type]}"
        :disabled="!countsPerType[type]"
        :ripple="false"
        @click="setFilter(type)"
      >
        <span class="sr-only">Show </span>{{ filterTypes[type].tab }}
      </v-btn>
    </v-btn-toggle>
    <div v-if="!currentUser.isAdmin && currentUser.canAccessAdvisingData" class="ms-auto">
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
    </div>
  </div>
  <EditBatchNoteModal
    v-if="isEditingNote"
    initial-mode="createNote"
    :on-close="onModalClose"
    :sid="student.sid"
  />
</template>

<script setup>
import {mdiFileDocument} from '@mdi/js'
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

<!--
<style scoped>
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
-->
