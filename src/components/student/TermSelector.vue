<template>
  <div v-if="isReady" class="align-center d-flex pb-2 pr-3">
    <label id="term-select-label" class="font-size-16 pr-2 text-medium-emphasis" for="students-term-select">
      <span class="sr-only">Select </span>Term
    </label>
    <v-select
      id="students-term-select"
      class="students-term-select"
      density="compact"
      eager
      hide-details
      item-title="label"
      :items="options"
      :model-value="selectedOption"
      single-line
      variant="outlined"
      @update:menu="onToggleMenu"
      @update:model-value="onSelectTerm"
    >
      <template #selection="{item}">
        <div class="text-no-wrap">
          <template v-if="item">
            <span class="sr-only">Showing enrollments for </span>{{ selectedOption.label }}<span class="sr-only">. Hit enter to open menu</span>
          </template>
          <template v-else>Select...</template>
        </div>
      </template>
      <template #item="{props, item}">
        <v-list-item
          :id="`term-select-option-${item.value}`"
          v-bind="props"
          class="min-height-unset py-1 pl-8"
          density="compact"
          role="option"
          :title="item.title"
        ></v-list-item>
      </template>
    </v-select>
  </div>
</template>

<script setup>
import {get, map} from 'lodash'
import {useContextStore} from '@/stores/context'
</script>

<script>
import {nextTick} from 'vue'
import {previousSisTermId, termNameForSisId} from '@/berkeley'

export default {
  name: 'TermSelector',
  props: {
    domain: {
      default: undefined,
      required: false,
      type: String
    }
  },
  data: () => ({
    isReady: false,
    options: []
  }),
  computed: {
    selectedOption() {
      return this.termOptionForId(get(useContextStore().currentUser, 'preferences.termId'))
    }
  },
  created() {
    this.options = this.getTermOptions()
    this.isReady = true
  },
  methods: {
    getTermOptions() {
      const currentTermId = `${useContextStore().config.currentEnrollmentTermId}`
      const termIds = [
        this.nextSisTermId(this.nextSisTermId(currentTermId)),
        this.nextSisTermId(currentTermId),
        currentTermId,
        previousSisTermId(currentTermId),
        previousSisTermId(previousSisTermId(currentTermId))
      ]
      return map(termIds, this.termOptionForId)
    },
    nextSisTermId(termId) {
      let nextTermId = ''
      let strTermId = termId.toString()
      switch (strTermId.slice(3)) {
      case '2':
        nextTermId = strTermId.slice(0, 3) + '5'
        break
      case '5':
        nextTermId = strTermId.slice(0, 3) + '8'
        break
      case '8':
        nextTermId =
          (parseInt(strTermId.slice(0, 3), 10) + 1).toString() + '2'
        break
      default:
        break
      }
      return nextTermId
    },
    onSelectTerm(value) {
      if (value !== get(useContextStore().currentUser, 'preferences.termId')) {
        useContextStore().updateCurrentUserPreference('termId', value)
        useContextStore().broadcast('termId-user-preference-change', value)
        nextTick(() => {
          useContextStore().alertScreenReader(`${this.selectedOption.label} selected`)
        })
      }
    },
    onToggleMenu(isOpen) {
      useContextStore().alertScreenReader(`Term menu ${isOpen ? 'opened' : 'closed'}`)
    },
    termOptionForId(termId) {
      let label = termNameForSisId(termId)
      if (termId === `${useContextStore().config.currentEnrollmentTermId}`) {
        label += ' (current)'
      }
      return {
        label: label,
        value: termId
      }
    }
  }
}
</script>

<style scoped>
.students-term-select {
  min-width: 310px;
}
</style>
