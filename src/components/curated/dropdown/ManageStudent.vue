<template>
  <div :class="{'sr-only': srOnly && !isAdding && !isRemoving && !showModal}">
    <b-dropdown
      :id="`curated-group-dropdown-${student.sid}`"
      :aria-label="`Curated groups for ${student.name}`"
      :class="{'p-0': isButtonVariantLink}"
      :disabled="disableSelector"
      :menu-class="isButtonVariantLink ? '' : 'groups-menu-class'"
      no-caret
      size="sm"
      :toggle-class="isButtonVariantLink ? '' : 'b-dd-override b-dd-narrow'"
      :variant="dropdownVariant"
    >
      <template slot="button-content">
        <div :id="isAdding ? 'added-to-curated-group' : (isRemoving ? 'removed-from-curated-group' : 'add-to-curated-group')">
          <div v-if="!isAdding && !isRemoving" class="d-flex justify-content-between">
            <div :class="{'font-size-14': isButtonVariantLink, 'pl-3': !isButtonVariantLink}">Add to Group</div>
            <div v-if="!isButtonVariantLink" class="pr-2">
              <font-awesome v-if="disableSelector || groupsLoading" icon="spinner" spin />
              <font-awesome v-if="!disableSelector && !groupsLoading" icon="caret-down" />
            </div>
          </div>
          <span v-if="isRemoving" :class="{'text-danger': isButtonVariantLink}">
            <font-awesome icon="times" /> Removed
          </span>
          <span v-if="isAdding" :class="{'text-success': isButtonVariantLink}">
            <font-awesome icon="check" /> Added
          </span>
        </div>
      </template>
      <b-dropdown-item v-if="!$_.size(myCuratedGroups)">
        <span class="text-nowrap pb-1 pl-3 pr-3 pt-1 faint-text">You have no curated groups.</span>
      </b-dropdown-item>
      <div v-if="!groupsLoading" class="pt-1">
        <b-dropdown-item
          v-for="group in myCuratedGroups"
          :id="`curated-group-${group.id}-menu-item`"
          :key="group.id"
          class="b-dd-item-override"
          @click="groupCheckboxClick(group)"
          @keyup.enter="groupCheckboxClick(group)"
        >
          <b-form-checkbox
            :id="`curated-group-${group.id}-checkbox`"
            v-model="checkedGroups"
            :aria-label="$_.includes(checkedGroups, group.id) ? `Remove ${student.name} from '${group.name}' group` : `Add ${student.name} to '${group.name}' group`"
            :value="group.id"
          >
            <span class="sr-only">Curated group </span>{{ group.name }}<span class="sr-only"> {{ checkedGroups.includes(group.id) ? 'is' : 'is not' }} selected</span>
          </b-form-checkbox>
        </b-dropdown-item>
      </div>
      <b-dropdown-divider />
      <b-dropdown-item
        id="create-curated-group"
        aria-label="Create a new curated group"
        class="create-new-button mb-0 pl-0 text-dark"
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
      <CreateCuratedGroupModal :cancel="onModalCancel" :create="onCreateCuratedGroup" />
    </b-modal>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import CreateCuratedGroupModal from '@/components/curated/CreateCuratedGroupModal'
import CurrentUserExtras from '@/mixins/CurrentUserExtras'
import Scrollable from '@/mixins/Scrollable'
import Util from '@/mixins/Util'
import {
  addStudents,
  createCuratedGroup,
  getMyCuratedGroupIdsPerStudentId,
  removeFromCuratedGroup
} from '@/api/curated'

export default {
  name: 'ManageStudent',
  components: {
    CreateCuratedGroupModal
  },
  mixins: [Context, CurrentUserExtras, Scrollable, Util],
  props: {
    srOnly: {
      required: false,
      type: Boolean
    },
    isButtonVariantLink: {
      required: false,
      type: Boolean
    },
    student: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    checkedGroups: undefined,
    confirmationTimeout: 1500,
    groupsLoading: true,
    isAdding: false,
    isRemoving: false,
    showModal: false
  }),
  computed: {
    disableSelector() {
      return this.isAdding || this.isRemoving
    },
    dropdownVariant() {
      return this.isButtonVariantLink ? 'link' : (this.isAdding ? 'success' : (this.isRemoving ? 'warning' : 'primary'))
    }
  },
  created() {
    this.refresh().then(() => {
      this.$eventHub.on('my-curated-groups-updated', this.refresh)
    })
  },
  methods: {
    groupCheckboxClick(group) {
      if (this.$_.includes(this.checkedGroups, group.id)) {
        this.isRemoving = true
        const done = () => {
          this.checkedGroups = this.$_.without(this.checkedGroups, group.id)
          this.isRemoving = false
          this.putFocusNextTick(`curated-group-dropdown-${this.student.sid}`, 'button')
          this.alertScreenReader(`${this.student.name} removed from "${group.name}"`)
          this.$ga.curatedEvent(group.id, group.name, `Student profile: Removed SID ${this.student.sid}`)
        }
        removeFromCuratedGroup(group.id, this.student.sid).finally(() =>
          setTimeout(done, this.confirmationTimeout)
        )
      } else {
        this.isAdding = true
        const done = () => {
          this.checkedGroups.push(group.id)
          this.isAdding = false
          this.putFocusNextTick(`curated-group-dropdown-${this.student.sid}`, 'button')
          this.alertScreenReader(`${this.student.name} added to "${group.name}"`)
          this.$ga.curatedEvent(group.id, group.name, `Student profile: Added SID ${this.student.sid}`)
        }
        addStudents(group.id, [this.student.sid]).finally(() => setTimeout(done, this.confirmationTimeout))
      }
    },
    onCreateCuratedGroup(name) {
      this.isAdding = true
      this.showModal = false
      const done = () => {
        this.putFocusNextTick(`curated-group-dropdown-${this.student.sid}`, 'button')
        this.isAdding = false
      }
      createCuratedGroup(name, [this.student.sid]).then(group => {
        this.checkedGroups.push(group.id)
        this.alertScreenReader(`${this.student.name} added to new curated group, "${name}".`)
        this.$_.each(
          [
            'create',
            `Student profile: Added SID ${this.student.sid}, after create group`
          ],
          action => {
            this.$ga.curatedEvent(group.id, group.name, action)
          }
        )
        setTimeout(done, this.confirmationTimeout)
      })
    },
    onModalCancel() {
      this.showModal = false
      this.alertScreenReader('Cancelled')
      this.putFocusNextTick(`curated-group-dropdown-${this.student.sid}`, 'button')
    },
    refresh() {
      return getMyCuratedGroupIdsPerStudentId(this.student.sid).then(data => {
        this.checkedGroups = data
        this.groupsLoading = false
      })
    }
  }
}
</script>

<style scoped>
.create-new-button {
  font-size: 16px;
}
.groups-menu-class {
  height: 35px !important;
  min-width: 160px !important;
  width: 160px !important;
}
</style>
