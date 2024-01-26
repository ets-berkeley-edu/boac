<template>
  <div v-if="isReady" class="align-items-center d-flex pb-1">
    <div>
      <label id="term-select-label" class="font-size-16 mb-0 pr-2 text-secondary" for="students-term-select">
        <span class="sr-only">Select </span>Term
      </label>
    </div>
    <div class="dropdown">
      <b-dropdown
        id="students-term-select"
        aria-labelledby="term-select-label"
        block
        left
        menu-class="w-100"
        no-caret
        toggle-class="dd-override"
        variant="link"
        @hidden="$announcer.polite('Term select menu closed')"
        @shown="$announcer.polite('Term select menu opened')"
      >
        <template #button-content>
          <div class="d-flex dropdown-width justify-content-between text-dark">
            <div v-if="selectedTermLabel">
              <span class="sr-only">Showing enrollments for </span>{{ selectedTermLabel }}<span class="sr-only">. Hit enter to open menu</span>
            </div>
            <div v-if="!selectedTermLabel">Select...</div>
            <div class="ml-2">
              <font-awesome icon="angle-down" class="menu-caret" />
            </div>
          </div>
        </template>
        <b-dropdown-item-button
          v-for="(option, index) in selectTermOptions"
          :id="`term-select-option-${option.value}`"
          :key="`select-term-option-${index}`"
          @click="onSelectTerm(option.value)"
        >
          {{ option.label }}
        </b-dropdown-item-button>
      </b-dropdown>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import store from '@/store'
import Util from '@/mixins/Util'
import {previousSisTermId, termNameForSisId} from '@/berkeley'

export default {
  name: 'TermSelector',
  mixins: [Context, Util],
  props: {
    domain: {
      default: undefined,
      required: false,
      type: String
    }
  },
  data: () => ({
    isReady: false,
    selectTermOptions: undefined,
    selectedTermId: undefined,
    selectedTermLabel: undefined,
  }),
  created() {
    this.selectTermOptions = this.getSelectTermOptions()
    this.setEventHandler(`${this.sortByKey}-user-preference-change`, v => this.selectedTermId = v)
    const selectedTermOption = this.termOptionForId(this._get(this.currentUser.preferences, 'termId'))
    this.selectedTermId = selectedTermOption.value
    this.selectedTermLabel = selectedTermOption.label
    this.isReady = true
  },
  methods: {
    getSelectTermOptions() {
      const currentTermId = `${this.config.currentEnrollmentTermId}`
      const termIds = [
        this.nextSisTermId(this.nextSisTermId(currentTermId)),
        this.nextSisTermId(currentTermId),
        currentTermId,
        previousSisTermId(currentTermId),
        previousSisTermId(previousSisTermId(currentTermId))
      ]
      return this._map(termIds, this.termOptionForId)
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
      if (value !== this._get(this.currentUser.preferences, 'termId')) {
        this.selectedTermId = value
        this.selectedTermLabel = termNameForSisId(value)
        this.$announcer.polite(`${this.selectedTermLabel} selected`)
        store.commit('context/updateCurrentUserPreference', {key: 'termId', value: this.selectedTermId})
        this.broadcast('termId-user-preference-change', value)
      }
    },
    termOptionForId(termId) {
      let label = termNameForSisId(termId)
      if (termId === `${this.config.currentEnrollmentTermId}`) {
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
.dropdown {
  background-color: #fefefe;
  border: 1px solid #ccc;
  border-radius: 4px;
  color: #000;
  height: 42px;
  text-align: left;
  vertical-align: middle;
  white-space: nowrap;
  width: 280px;
}
</style>
