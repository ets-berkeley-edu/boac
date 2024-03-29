<template>
  <div :class="{'opacity-zero': srOnly && !isAdding && !isRemoving && !showModal}">
    <v-menu
      :id="dropdownId"
      :aria-label="`${domainLabel(true)}s for ${student.name}`"
      :class="{'pa-0': isButtonVariantLink}"
      :disabled="disableSelector"
      :menu-class="isButtonVariantLink ? '' : 'groups-menu-class'"
      no-caret
      :right="alignDropdownRight"
      size="sm"
      :toggle-class="isButtonVariantLink ? '' : 'b-dd-override b-dd-narrow btn-primary-color-override'"
      :variant="dropdownVariant"
    >
      <template #activator="{props}">
        <v-btn
          :id="isAdding ? `added-to-${idFragment}` : (isRemoving ? `removed-from-${idFragment}` : `add-to-${idFragment}`)"
          v-bind="props"
        >
          <div v-if="!isAdding && !isRemoving" class="d-flex justify-content-between">
            <div :class="labelClass">
              {{ label }}
            </div>
            <div v-if="!isButtonVariantLink" class="pr-2">
              <v-progress-circular
                v-if="disableSelector || groupsLoading"
                indeterminate
                size="small"
              />
              <v-icon v-if="!disableSelector && !groupsLoading" :icon="mdiMenuDown" />
            </div>
          </div>
          <span v-if="isRemoving" :class="{'text-danger': isButtonVariantLink, 'text-white': !isButtonVariantLink}">
            <v-icon :icon="mdiClose" /> Removed
          </span>
          <span v-if="isAdding" :class="{'text-success': isButtonVariantLink}">
            <v-icon :icon="mdiCheckBold" /> Added
          </span>
        </v-btn>
      </template>
      <v-card min-width="300">
        <v-list>
          <v-list-item v-if="!_filter(currentUser.myCuratedGroups, ['domain', domain]).length">
            <span class="text-no-wrap pb-1 pl-3 pr-3 pt-1 faint-text">You have no {{ domainLabel(false) }}s.</span>
          </v-list-item>
          <div v-if="!groupsLoading" class="pt-1">
            <v-list-item
              v-for="group in _filter(currentUser.myCuratedGroups, ['domain', domain])"
              :id="`${idFragment}-${group.id}-menu-item`"
              :key="group.id"
              @click="groupCheckboxClick(group)"
              @keyup.enter="groupCheckboxClick(group)"
            >
              <v-checkbox
                :id="`${idFragment}-${group.id}-checkbox`"
                v-model="checkedGroups"
                :aria-label="_includes(checkedGroups, group.id) ? `Remove ${student.name} from '${group.name}' group` : `Add ${student.name} to '${group.name}' group`"
                :value="group.id"
              >
                <span class="sr-only">{{ domainLabel(true) }} </span>{{ group.name }}<span class="sr-only"> {{ checkedGroups.includes(group.id) ? 'is' : 'is not' }} selected</span>
              </v-checkbox>
            </v-list-item>
          </div>
          <v-divider />
          <v-list-item
            :id="`create-${idFragment}`"
            :aria-label="`Create a new ${domainLabel(false)}`"
            class="create-new-button mb-0 pl-0 text-dark"
            @click="showModal = true"
          >
            <v-icon :icon="mdiPlus" /> Create New {{ domainLabel(true) }}
          </v-list-item>
        </v-list>
      </v-card>
    </v-menu>
    <v-dialog
      v-model="showModal"
      body-class="pl-0 pr-0"
      hide-footer
      hide-header
      @shown="putFocusNextTick('modal-header')"
    >
      <CreateCuratedGroupModal
        :cancel="onModalCancel"
        :create="onCreateCuratedGroup"
        :domain="domain"
      />
    </v-dialog>
  </div>
</template>

<script setup>
import {mdiCheckBold, mdiClose, mdiMenuDown, mdiPlus} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import CreateCuratedGroupModal from '@/components/curated/CreateCuratedGroupModal'
import Util from '@/mixins/Util'
import {
  addStudentsToCuratedGroup,
  createCuratedGroup,
  removeFromCuratedGroup
} from '@/api/curated'
import {describeCuratedGroupDomain} from '@/berkeley'

export default {
  name: 'ManageStudent',
  components: {
    CreateCuratedGroupModal
  },
  mixins: [Context, Util],
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
    this.setEventHandler('my-curated-groups-updated', this.onUpdateMyCuratedGroups)
  },
  unmounted() {
    this.removeEventHandler('my-curated-groups-updated', this.onUpdateMyCuratedGroups)
  },
  methods: {
    domainLabel(capitalize) {
      return describeCuratedGroupDomain(this.domain, capitalize)
    },
    groupCheckboxClick(group) {
      if (this._includes(this.checkedGroups, group.id)) {
        this.isRemoving = true
        const done = () => {
          this.checkedGroups = this._without(this.checkedGroups, group.id)
          this.isRemoving = false
          this.putFocusNextTick(this.dropdownId, 'button')
          this.alertScreenReader(`${this.student.name} removed from "${group.name}"`)
        }
        removeFromCuratedGroup(group.id, this.student.sid).finally(() =>
          setTimeout(done, this.confirmationTimeout)
        )
      } else {
        this.isAdding = true
        const done = () => {
          this.checkedGroups.push(group.id)
          this.isAdding = false
          this.putFocusNextTick(this.dropdownId, 'button')
          this.alertScreenReader(`${this.student.name} added to "${group.name}"`)
        }
        addStudentsToCuratedGroup(group.id, [this.student.sid]).finally(() => setTimeout(done, this.confirmationTimeout))
      }
    },
    onCreateCuratedGroup(name) {
      this.isAdding = true
      this.showModal = false
      const done = () => {
        this.putFocusNextTick(this.dropdownId, 'button')
        this.isAdding = false
      }
      createCuratedGroup(this.domain, name, [this.student.sid]).then(group => {
        this.checkedGroups.push(group.id)
        this.alertScreenReader(`${this.student.name} added to new ${this.domainLabel(false)}, "${name}".`)
        setTimeout(done, this.confirmationTimeout)
      })
    },
    onModalCancel() {
      this.showModal = false
      this.alertScreenReader('Canceled')
      this.putFocusNextTick(this.dropdownId, 'button')
    },
    onUpdateMyCuratedGroups(domain) {
      if (domain === this.domain) {
        this.refresh()
      }
    },
    refresh() {
      const containsSid = group => {
        return this._includes(group.sids, this.student.sid)
      }
      this.checkedGroups = this._map(this._filter(this.currentUser.myCuratedGroups, containsSid), 'id')
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
