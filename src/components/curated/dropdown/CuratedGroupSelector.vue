<template>
  <div class="d-flex">
    <label id="add-all-checkbox-label" :for="checkboxId" class="sr-only">
      Select all students to add to a {{ domainLabel(false) }}
    </label>
    <div class="add-all-checkbox">
      <b-form-checkbox
        :id="checkboxId"
        v-model="isSelectAllChecked"
        :aria-controls="dropdownId"
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
        :id="dropdownId"
        :variant="isSaving ? 'success' : 'primary'"
        :disabled="isSaving"
        class="curated-selector mr-2"
        toggle-class="b-dd-override"
        size="sm"
        no-caret
      >
        <template slot="button-content">
          <div
            :id="isSaving ? `add-to-${domain === 'admitted_students' ? 'admissions' : 'curated'}-group-confirmation` : `add-to-${domain === 'admitted_students' ? 'admissions' : 'curated'}-group`"
            class="px-1"
          >
            <div v-if="!isSaving" class="d-flex justify-content-between">
              <div class="pr-2">Add to {{ domainLabel(true) }}</div>
              <div>
                <font-awesome v-if="isSaving" icon="spinner" spin />
                <font-awesome v-if="!isSaving" icon="caret-down" />
              </div>
            </div>
            <div v-if="isSaving">
              <font-awesome icon="check" /> Added to {{ domainLabel(true) }}
            </div>
          </div>
        </template>
        <b-dropdown-item v-if="!myCuratedGroups.length">
          <span class="text-nowrap pb-1 pl-3 pr-3 pt-1 faint-text">You have no {{ domainLabel(false) }}s.</span>
        </b-dropdown-item>
        <b-dropdown-item
          v-for="group in myCuratedGroups"
          :key="group.id"
          class="b-dd-item-override"
          @click="curatedGroupCheckboxClick(group)"
        >
          <b-form-checkbox
            :id="`${domain === 'admitted_students' ? 'admissions' : 'curated'}-group-${group.id}-checkbox`"
            @click="curatedGroupCheckboxClick(group)"
            @keyup.enter="curatedGroupCheckboxClick(group)"
          >
            <span class="sr-only">Hit enter to add students to </span>{{ group.name }}
          </b-form-checkbox>
        </b-dropdown-item>
        <b-dropdown-divider />
        <b-dropdown-item
          :id="`create--${domain === 'admitted_students' ? 'admissions' : 'curated'}-group`"
          :aria-label="`Create a new ${domainLabel(false)}`"
          class="pl-0 text-dark"
          variant="link"
          @click="showModal = true"
        >
          <font-awesome icon="plus" />
          Create New {{ domainLabel(true) }}
        </b-dropdown-item>
      </b-dropdown>
      <b-modal
        v-model="showModal"
        body-class="pl-0 pr-0"
        hide-footer
        hide-header
        @shown="$putFocusNextTick('modal-header')"
      >
        <CreateCuratedGroupModal
          :cancel="modalCancel"
          :create="modalCreateCuratedGroup"
          :domain="domain"
        />
      </b-modal>
    </div>
  </div>
</template>

<script>
import CreateCuratedGroupModal from '@/components/curated/CreateCuratedGroupModal'
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import {addStudents, createCuratedGroup} from '@/api/curated'


export default {
  name: 'CuratedGroupSelector',
  components: {CreateCuratedGroupModal},
  mixins: [Context, Util],
  props: {
    contextDescription: {
      required: true,
      type: String
    },
    domain: {
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
    checkboxId: undefined,
    dropdownId: undefined,
    sids: [],
    isSelectAllChecked: false,
    indeterminate: false,
    isSaving: false,
    showModal: false
  }),
  computed: {
    myCuratedGroups() {
      return this.$_.filter(this.$currentUser.myCuratedGroups, ['domain', this.domain])
    }
  },
  created() {
    this.checkboxId = `add-all-to-${this.domain}-curated-group`
    this.dropdownId = `${this.domain === 'admitted_students' ? 'admissions' : 'curated'}-group-dropdown-select`
    this.$eventHub.on('curated-group-checkbox-checked', args => {
      if (this.domain === args.domain) {
        this.sids.push(args.sid)
        this.refresh()
      }
    })
    this.$eventHub.on('curated-group-checkbox-unchecked', args => {
      if (this.domain === args.domain) {
        this.sids = this.$_.remove(this.sids, s => s !== args.sid)
        this.refresh()
      }
    })
  },
  methods: {
    afterAddStudents(group) {
      this.$announcer.polite(`${this.sids.length} student${this.sids.length === 1 ? '' : 's'} added to ${this.domainLabel(true)} "${group.name}".`)
      this.sids = []
      this.isSelectAllChecked = this.indeterminate = false
      this.$eventHub.emit('curated-group-deselect-all', this.domain)
      this.$ga.curatedEvent(group.id, group.name, `${this.contextDescription}: add students to ${this.domainLabel(true)}`)
    },
    afterCreateGroup() {
      this.sids = []
      this.refresh()
      this.toggle(false)
      this.$putFocusNextTick(this.checkboxId)
      this.onCreateCuratedGroup()
    },
    afterCreateGroupModalCancel() {
      this.sids = []
      this.refresh()
      this.toggle(false)
      this.$putFocusNextTick(this.checkboxId)
    },
    curatedGroupCheckboxClick(group) {
      this.isSaving = true
      const done = () => {
        this.isSaving = false
      }
      addStudents(group.id, this.sids)
        .then(() => {
          this.afterAddStudents(group)
        }).finally(() => setTimeout(done, 2000))
    },
    domainLabel(capitalize) {
      return this.describeCuratedGroupDomain(this.domain, capitalize)
    },
    refresh() {
      this.indeterminate = this.$_.inRange(this.$_.size(this.sids), 1, this.$_.size(this.students))
      this.isSelectAllChecked = this.$_.size(this.sids) === this.$_.size(this.students)
    },
    modalCancel() {
      this.showModal = false
      this.$announcer.polite('Canceled')
    },
    modalCreateCuratedGroup(name) {
      this.isSaving = true
      this.showModal = false
      let done = () => {
        this.isSaving = false
        this.$announcer.polite(`Student${this.sids.length === 1 ? 's' : ''} added to ${this.domainLabel(false)} ${name}`)
        this.afterCreateGroup()
      }
      const trackEvent = group => {
        this.$_.each(
          [
            'create',
            `${this.contextDescription}: add student${this.sids.length === 1 ? 's' : ''} to ${this.domainLabel(true)}`
          ],
          action => {
            this.$ga.curatedEvent(group.id, group.name, action)
          }
        )
      }
      createCuratedGroup(this.domain, name, this.sids)
        .then(trackEvent)
        .finally(() => setTimeout(() => done(), 2000))
    },
    toggle(checked) {
      this.sids = []
      if (checked) {
        this.$_.each(this.students, student => {
          this.sids.push(student.sid || student.csEmplId)
        })
        this.$eventHub.emit('curated-group-select-all', this.domain)
        this.$putFocusNextTick(this.dropdownId, 'button')
        this.$announcer.polite('All students on this page selected.')
      } else {
        this.$eventHub.emit('curated-group-deselect-all', this.domain)
        this.$announcer.polite('All students on this page deselected.')
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
  padding: 2px 2px 0 7px;
  width: 36px;
}
.curated-selector {
  height: 35px;
}
</style>
