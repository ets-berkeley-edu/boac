<template>
  <div>
    <div class="py-2">
      <label
        :for="`batch-note-${type}`"
        class="font-size-14 font-weight-bold"
      >
        <span class="sr-only">Select a </span>{{ header }}
      </label>
    </div>
    <v-select
      :id="`batch-note-${type}`"
      v-model="added"
      :aria-label="`Note will be created for all students in selected ${type}${objects.length === 1 ? '' : 's'}`"
      class="mb-2 ml-0 transparent"
      density="compact"
      :disabled="disabled"
      hide-details
      hide-selected
      item-title="name"
      item-value="id"
      :items="objects"
      :label="isCuratedGroupsMode ? 'Add Group' : 'Add Cohort'"
      multiple
      return-object
      single-line
      variant="outlined"
      menu-class="batch-note-cohorts-dropdown"
    >
      <template #item="{props, item}">
        <v-list-item v-bind="props">
          <template #title="{title}">
            <span
              :id="`batch-note-${type}-option-${item.value}`"
              :key="item.value"
              :aria-label="`Add ${type} ${title}`"
              @click.stop="addItem(item.raw)"
            >
              {{ title }}
            </span>
          </template>
        </v-list-item>
      </template>
      <template #selection="{item, index}">
        <v-chip
          :id="`batch-note-${type}-${index}`"
          class="font-weight-bold text-medium-emphasis text-uppercase text-nowrap"
          closable
          :close-label="`Remove ${type} ${item.title}`"
          density="comfortable"
          variant="outlined"
          @click:close="remove(item.raw)"
        >
          {{ item.title }}
          <template #close>
            <v-icon color="error" :icon="mdiCloseCircle"></v-icon>
          </template>
        </v-chip>
      </template>
    </v-select>
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
      if (!this.addedIds.includes(object.id)) {
        this.added.push(object)
        this.addObject(object)
      }
    },
    remove(object) {
      const index = this._findIndex(this.added, {'id': object.id})
      this.added.splice(index, 1)
      this.removeObject(object)
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
