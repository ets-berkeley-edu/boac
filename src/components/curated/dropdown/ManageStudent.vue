<template>
  <div :class="{'opacity-zero': srOnly && !isAdding && !isRemoving && !showModal}">
    <b-dropdown
      :id="dropdownId"
      :aria-label="`${domainLabel(true)}s for ${student.name}`"
      :class="{'p-0': isButtonVariantLink}"
      :disabled="disableSelector"
      :menu-class="isButtonVariantLink ? '' : 'groups-menu-class'"
      no-caret
      :right="alignDropdownRight"
      size="sm"
      :toggle-class="isButtonVariantLink ? '' : 'b-dd-override b-dd-narrow btn-primary-color-override'"
      :variant="dropdownVariant"
    >
      <template slot="button-content">
        <div :id="isAdding ? `added-to-${idFragment}` : (isRemoving ? `removed-from-${idFragment}` : `add-to-${idFragment}`)">
          <div v-if="!isAdding && !isRemoving" class="d-flex justify-content-between">
            <div :class="labelClass">
              {{ label }}
            </div>
            <div v-if="!isButtonVariantLink" class="pr-2">
              <font-awesome v-if="disableSelector || groupsLoading" icon="spinner" spin />
              <font-awesome v-if="!disableSelector && !groupsLoading" icon="caret-down" />
            </div>
          </div>
          <span v-if="isRemoving" :class="{'text-danger': isButtonVariantLink, 'text-white': !isButtonVariantLink}">
            <font-awesome icon="times" /> Removed
          </span>
          <span v-if="isAdding" :class="{'text-success': isButtonVariantLink}">
            <font-awesome icon="check" /> Added
          </span>
        </div>
      </template>
      <b-dropdown-item v-if="!$_.filter($currentUser.myCuratedGroups, ['domain', domain]).length">
        <span class="text-nowrap pb-1 pl-3 pr-3 pt-1 faint-text">You have no {{ domainLabel(false) }}s.</span>
      </b-dropdown-item>
      <div v-if="!groupsLoading" class="pt-1">
        <b-dropdown-item
          v-for="group in $_.filter($currentUser.myCuratedGroups, ['domain', domain])"
          :id="`${idFragment}-${group.id}-menu-item`"
          :key="group.id"
          class="b-dd-item-override"
          @click="groupCheckboxClick(group)"
          @keyup.enter="groupCheckboxClick(group)"
        >
          <b-form-checkbox
            :id="`${idFragment}-${group.id}-checkbox`"
            v-model="checkedGroups"
            :aria-label="$_.includes(checkedGroups, group.id) ? `Remove ${student.name} from '${group.name}' group` : `Add ${student.name} to '${group.name}' group`"
            :value="group.id"
          >
            <span class="sr-only">{{ domainLabel(true) }} </span>{{ group.name }}<span class="sr-only"> {{ checkedGroups.includes(group.id) ? 'is' : 'is not' }} selected</span>
          </b-form-checkbox>
        </b-dropdown-item>
      </div>
      <b-dropdown-divider />
      <b-dropdown-item
        :id="`create-${idFragment}`"
        :aria-label="`Create a new ${domainLabel(false)}`"
        class="create-new-button mb-0 pl-0 text-dark"
        @click="showModal = true"
      >
        <font-awesome icon="plus" /> Create New {{ domainLabel(true) }}
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
        :cancel="onModalCancel"
        :create="onCreateCuratedGroup"
        :domain="domain"
      />
    </b-modal>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import CreateCuratedGroupModal from '@/components/curated/CreateCuratedGroupModal'
import Scrollable from '@/mixins/Scrollable'
import Util from '@/mixins/Util'
import {
  addStudents,
  createCuratedGroup,
  removeFromCuratedGroup
} from '@/api/curated'

export default {
  name: 'ManageStudent',
  components: {
    CreateCuratedGroupModal
  },
  mixins: [Context, Scrollable, Util],
  props: {
    alignDropdownRight: {
      required: false,
      type: Boolean
    },
    domain: {
      required: true,
      type: String
    },
    isButtonVariantLink: {
      required: false,
      type: Boolean
    },
    label: {
      default: 'Add to Group',
      required: false,
      type: String
    },
    labelClass: {
      default: 'font-size-14 px-2',
      required: false,
      type: String
    },
    srOnly: {
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
    dropdownId: undefined,
    groupsLoading: true,
    idFragment: undefined,
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
    this.idFragment = this.domainLabel(false).replace(' ', '-')
    this.dropdownId = `${this.idFragment}-dropdown-${this.student.sid}`
    this.refresh()
    this.$eventHub.on('my-curated-groups-updated', domain => {
      if (domain === this.domain) {
        this.refresh()
      }
    })
  },
  methods: {
    domainLabel(capitalize) {
      return this.describeCuratedGroupDomain(this.domain, capitalize)
    },
    groupCheckboxClick(group) {
      if (this.$_.includes(this.checkedGroups, group.id)) {
        this.isRemoving = true
        const done = () => {
          this.checkedGroups = this.$_.without(this.checkedGroups, group.id)
          this.isRemoving = false
          this.$putFocusNextTick(this.dropdownId, 'button')
          this.$announcer.polite(`${this.student.name} removed from "${group.name}"`)
        }
        removeFromCuratedGroup(group.id, this.student.sid).finally(() =>
          setTimeout(done, this.confirmationTimeout)
        )
      } else {
        this.isAdding = true
        const done = () => {
          this.checkedGroups.push(group.id)
          this.isAdding = false
          this.$putFocusNextTick(this.dropdownId, 'button')
          this.$announcer.polite(`${this.student.name} added to "${group.name}"`)
        }
        addStudents(group.id, [this.student.sid]).finally(() => setTimeout(done, this.confirmationTimeout))
      }
    },
    onCreateCuratedGroup(name) {
      this.isAdding = true
      this.showModal = false
      const done = () => {
        this.$putFocusNextTick(this.dropdownId, 'button')
        this.isAdding = false
      }
      createCuratedGroup(this.domain, name, [this.student.sid]).then(group => {
        this.checkedGroups.push(group.id)
        this.$announcer.polite(`${this.student.name} added to new ${this.domainLabel(false)}, "${name}".`)
        setTimeout(done, this.confirmationTimeout)
      })
    },
    onModalCancel() {
      this.showModal = false
      this.$announcer.polite('Canceled')
      this.$putFocusNextTick(this.dropdownId, 'button')
    },
    refresh() {
      const containsSid = group => {
        return this.$_.includes(group.sids, this.student.sid)
      }
      this.checkedGroups = this.$_.map(this.$_.filter(this.$currentUser.myCuratedGroups, containsSid), 'id')
      this.groupsLoading = false
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
.opacity-zero {
  opacity: 0;
}
</style>
