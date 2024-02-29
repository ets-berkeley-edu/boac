<template>
  <div>
    <div>
      <label
        :for="`batch-note-${type}`"
        class="font-size-14 font-weight-bolder input-label text mt-2"
      ><span class="sr-only">Select a </span>{{ header }}</label>
    </div>
    <select
      :id="`batch-note-${type}`"
      :disabled="disabled"
      dropright
      :text="isCuratedGroupsMode ? 'Add Group' : 'Add Cohort'"
      :aria-label="`Note will be created for all students in selected ${type}${objects.length === 1 ? '' : 's'}`"
      variant="outlined"
      class="mb-2 ml-0 transparent"
      menu-class="batch-note-cohorts-dropdown"
    >
      <option
        v-for="object in objects"
        :id="`batch-note-${type}-option-${object.id}`"
        :key="object.id"
        :aria-label="`Add ${type} ${object.name}`"
        :disabled="_includes(addedIds, object.id)"
        @click="addItem(object)"
      >
        {{ _truncate(object.name) }}
      </option>
    </select>
    <div>
      <div v-for="(addedObject, index) in added" :key="addedObject.id" class="mb-1">
        <span class="font-weight-bolder pill pill-attachment text-uppercase text-nowrap">
          <span :id="`batch-note-${type}-${index}`">{{ _truncate(addedObject.name) }}</span>
          <v-btn
            :id="`remove-${type}-from-batch-${index}`"
            variant="plain"
            class="p-0"
            @click.prevent="remove(addedObject)"
          >
            <v-icon :icon="mdiCloseCircle" class="font-size-20 has-error pl-2" />
            <span class="sr-only">Remove</span>
          </v-btn>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import {mdiCloseCircle} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'

export default {
  name: 'BatchNoteAddCohort',
  mixins: [Context, Util],
  props: {
    addObject: {
      required: true,
      type: Function
    },
    disabled: {
      required: false,
      type: Boolean
    },
    objects: {
      required: true,
      type: Array
    },
    isCuratedGroupsMode: {
      required: true,
      type: Boolean
    },
    removeObject: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    added: [],
    header: undefined,
    type: undefined
  }),
  computed: {
    addedIds() {
      return this._map(this.added, 'id')
    }
  },
  created() {
    this.header = this.isCuratedGroupsMode ? 'Curated Group' : 'Cohort'
    this.type = this.isCuratedGroupsMode ? 'curated' : 'cohort'
  },
  methods: {
    addItem(object) {
      this.added.push(object)
      this.addObject(object)
      this.alertScreenReader(`${this.header} ${object.name} added to batch note`)
    },
    remove(object) {
      this.added = this._filter(this.added, a => a.id !== object.id)
      this.removeObject(object)
      this.alertScreenReader(`${this.header} ${object.name} removed from batch note`)
    }
  }
}
</script>

<style>
.batch-note-cohorts-dropdown {
  max-height: 400px !important;
  overflow-y: scroll !important;
}
</style>
