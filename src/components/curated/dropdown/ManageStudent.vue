<template>
  <div :class="{'opacity-zero': srOnly && !isAdding && !isRemoving && !showModal}">
    <v-menu
      :id="dropdownId"
      :aria-label="`${domainLabel(true)}s for ${student.name}`"
      :class="{'groups-menu-class pa-0': isButtonVariantLink}"
      :disabled="disableSelector"
    >
      <template #activator="{props}">
        <v-btn
          :id="isAdding ? `added-to-${idFragment}` : (isRemoving ? `removed-from-${idFragment}` : `add-to-${idFragment}`)"
          v-bind="props"
          color="primary"
          size="x-small"
          variant="text"
        >
          <span v-if="!isAdding && !isRemoving" class="align-center d-flex justify-space-between">
            <div :class="labelClass">
              {{ label }}
            </div>
            <div v-if="!isButtonVariantLink">
              <v-progress-circular
                v-if="disableSelector || groupsLoading"
                indeterminate
                size="14"
                width="2"
              />
              <v-icon v-if="!disableSelector && !groupsLoading" :icon="mdiMenuDown" size="24" />
            </div>
          </span>
          <span v-if="isRemoving" :class="{'text-danger': isButtonVariantLink, 'text-white': !isButtonVariantLink}">
            <v-icon :icon="mdiClose" /> Removed
          </span>
          <span v-if="isAdding" :class="{'text-success': isButtonVariantLink}">
            <v-icon :icon="mdiCheckBold" /> Added
          </span>
        </v-btn>
      </template>
      <v-card v-if="!groupsLoading" density="compact">
        <v-list density="compact" variant="flat">
          <v-list-item v-if="!_filter(currentUser.myCuratedGroups, ['domain', domain]).length">
            <span class="text-grey px-3 py-1 text-no-wrap">You have no {{ domainLabel(false) }}s.</span>
          </v-list-item>
          <v-list-item
            v-for="group in _filter(currentUser.myCuratedGroups, ['domain', domain])"
            :key="group.id"
            density="compact"
            @click="groupCheckboxClick(group)"
            @keyup.enter="groupCheckboxClick(group)"
          >
            <template #prepend>
              <v-checkbox
                :id="`${idFragment}-${group.id}-checkbox`"
                v-model="checkedGroups"
                :aria-label="_includes(checkedGroups, group.id) ? `Remove ${student.name} from '${group.name}' group` : `Add ${student.name} to '${group.name}' group`"
                class="mr-2"
                density="compact"
                hide-details
                :value="group.id"
              >
                <span class="sr-only">{{ domainLabel(true) }} </span>
                {{ group.name }}<span class="sr-only"> {{ checkedGroups.includes(group.id) ? 'is' : 'is not' }} selected</span>
              </v-checkbox>
            </template>
          </v-list-item>
          <v-list-item class="border-t-sm mt-2 pt-2" density="compact">
            <v-btn
              :id="`create-${idFragment}`"
              :aria-label="`Create a new ${domainLabel(false)}`"
              :prepend-icon="mdiPlus"
              :text="`Create New ${domainLabel(true)}`"
              @click="showModal = true"
            />
          </v-list-item>
        </v-list>
      </v-card>
    </v-menu>
    <CreateCuratedGroupModal
      :cancel="onModalCancel"
      :create="onCreateCuratedGroup"
      :domain="domain"
      :show-modal="showModal"
    />
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
      default: 'font-size-14',
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
