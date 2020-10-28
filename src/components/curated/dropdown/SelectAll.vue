<template>
  <div class="d-flex">
    <label id="add-all-checkbox-label" for="add-all-to-curated-group" class="sr-only">
      Select all students to add to a curated group
    </label>
    <div class="add-all-checkbox">
      <b-form-checkbox
        id="add-all-to-curated-group"
        v-model="isSelectAllChecked"
        aria-controls="curated-group-dropdown-select"
        aria-labelledby="add-all-checkbox-label"
        :disabled="isSaving"
        :indeterminate="indeterminate"
        size="lg"
        @change="toggle"
      />
    </div>
    <div>
      <b-dropdown
        v-if="!!$_.size(sids)"
        id="curated-group-dropdown-select"
        :variant="isSaving ? 'success' : 'primary'"
        :disabled="disableSelector"
        class="curated-selector mr-2"
        toggle-class="b-dd-override"
        size="sm"
        no-caret>
        <template slot="button-content">
          <div :id="isSaving ? 'add-to-curated-group-confirmation' : 'add-to-curated-group'" class="px-1">
            <div v-if="!isSaving" class="d-flex justify-content-between">
              <div class="pr-2">Add to Curated Group</div>
              <div>
                <font-awesome v-if="disableSelector" icon="spinner" spin />
                <font-awesome v-if="!disableSelector" icon="caret-down" />
              </div>
            </div>
            <div v-if="isSaving">
              <font-awesome icon="check" /> Added to Curated Group
            </div>
          </div>
        </template>
        <b-dropdown-item v-if="!$_.size(myCuratedGroups)">
          <span class="text-nowrap pb-1 pl-3 pr-3 pt-1 faint-text">You have no curated groups.</span>
        </b-dropdown-item>
        <b-dropdown-item
          v-for="group in myCuratedGroups"
          :key="group.id"
          class="b-dd-item-override"
          @click="curatedGroupCheckboxClick(group)"
        >
          <b-form-checkbox
            :id="`curated-group-${group.id}-checkbox`"
            :aria-labelledby="`curated-group-${group.id}-checkbox`"
            @click="curatedGroupCheckboxClick(group)"
            @keyup.enter="curatedGroupCheckboxClick(group)">
            <span class="sr-only">Hit enter to add students to </span>{{ group.name }}
          </b-form-checkbox>
        </b-dropdown-item>
        <hr class="dropdown-divider">
        <b-dropdown-item
          id="create-curated-group"
          class="pl-0 text-dark"
          variant="link"
          aria-label="Create a new curated group"
          @click="showModal = true"
        >
          <font-awesome icon="plus" /> Create New Curated Group
        </b-dropdown-item>
      </b-dropdown>
      <b-modal
        v-model="showModal"
        body-class="pl-0 pr-0"
        hide-footer
        hide-header-close
        title="Create Curated Group"
        @shown="focusModalById('create-input')"
      >
        <CreateCuratedGroupModal :cancel="modalCancel" :create="modalCreateCuratedGroup" />
      </b-modal>
    </div>
  </div>
</template>

<script>
import CreateCuratedGroupModal from '@/components/curated/CreateCuratedGroupModal'
import Context from '@/mixins/Context'
import CurrentUserExtras from '@/mixins/CurrentUserExtras'
import Util from '@/mixins/Util'
import {addStudents, createCuratedGroup} from '@/api/curated'

export default {
  name: 'SelectAll',
  components: {CreateCuratedGroupModal},
  mixins: [Context, CurrentUserExtras, Util],
  props: {
    contextDescription: {
      required: true,
      type: String
    },
    gaEventTracker: {
      required: true,
      type: Function
    },
    onCreateCuratedGroup: {
      default: () => {},
      required: false,
      type: Function
    },
    students: {
      required: true,
      type: Array
    }
  },
  data: () => ({
    sids: [],
    isSelectAllChecked: false,
    indeterminate: false,
    isSaving: false,
    showModal: false
  }),
  computed: {
    disableSelector() {
      return this.isSaving || this.$_.isNil(this.myCuratedGroups)
    }
  },
  created() {
    this.$eventHub.on('curated-group-checkbox-checked', sid => {
      this.sids.push(sid)
      this.refresh()
    })
    this.$eventHub.on('curated-group-checkbox-unchecked', sid => {
      this.sids = this.$_.remove(this.sids, s => s !== sid)
      this.refresh()
    })
  },
  methods: {
    afterAddStudents(group) {
      this.alertScreenReader(`${this.sids.length} student${this.sids.length === 1 ? '' : 's'} added to Curated Group "${group.name}".`)
      this.sids = []
      this.isSelectAllChecked = this.indeterminate = false
      this.$eventHub.emit('curated-group-deselect-all')
      this.$ga.curatedEvent(group.id, group.name, `${this.contextDescription}: add students to Curated Group`)
    },
    afterCreateGroup() {
      this.sids = []
      this.refresh()
      this.toggle(false)
      this.putFocusNextTick('add-all-to-curated-group')
      this.onCreateCuratedGroup()
    },
    afterCreateGroupModalCancel() {
      this.sids = []
      this.refresh()
      this.toggle(false)
      this.putFocusNextTick('add-all-to-curated-group')
    },
    curatedGroupCheckboxClick(group) {
      this.isSaving = true
      const done = () => {
        this.isSaving = false
      }
      addStudents(group.id, this.sids)
        .then(() => {
          this.afterAddStudents(group)
        })
        .finally(() => setTimeout(done, 2000))
    },
    refresh() {
      this.indeterminate = this.$_.inRange(
        this.$_.size(this.sids),
        1,
        this.$_.size(this.students)
      )
      this.isSelectAllChecked = this.$_.size(this.sids) === this.$_.size(this.students)
    },
    modalCancel() {
      this.showModal = false
      this.alertScreenReader('Cancelled')
      this.afterModalCancel()
    },
    modalCreateCuratedGroup(name) {
      this.isSaving = true
      this.showModal = false
      let done = () => {
        this.isSaving = false
        this.alertScreenReader(`Student${this.sids.length === 1 ? 's' : ''} added to curated group ${name}`)
        this.afterCreateGroup()
      }
      const trackEvent = group => {
        this.$_.each(
          [
            'create',
            `${this.contextDescription}: add student${this.sids.length === 1 ? 's' : ''} to Curated Group`
          ],
          action => {
            this.$ga.curatedEvent(group.id, group.name, action)
          }
        )
      }
      createCuratedGroup(name, this.sids)
        .then(trackEvent)
        .finally(() => setTimeout(() => done(), 2000))
    },
    toggle(checked) {
      if (checked) {
        this.sids = this.$_.map(this.students, 'sid')
        this.$eventHub.emit('curated-group-select-all')
        this.putFocusNextTick('curated-group-dropdown-select', 'button')
        this.alertScreenReader('All students on this page selected.')
      } else {
        this.sids = []
        this.$eventHub.emit('curated-group-deselect-all')
        this.alertScreenReader('All students on this page deselected.')
      }
    }
  }
}
</script>

<style scoped>
label {
  font-size: 14px;
  margin-bottom: 0;
}
.add-all-checkbox {
  background-color: #eee;
  border: 1px solid #aaa;
  border-radius: 6px;
  height: 36px;
  padding-left: 7px;
  padding-top: 2px;
  width: 36px;
}
.curated-selector {
  height: 35px;
}
</style>
