<template>
  <div :class="{'opacity-zero': srOnly && !isAdding && !isRemoving && !showModal}">
    <v-menu
      :id="dropdownId"
      :aria-label="`${domainLabel(true)}s for ${student.name}`"
      :disabled="disableSelector"
    >
      <template #activator="{props}">
        <v-btn
          :id="isAdding ? `added-to-${idFragment}` : (isRemoving ? `removed-from-${idFragment}` : `add-to-${idFragment}`)"
          v-bind="props"
          class="manage-student-btn"
          :color="buttonColor"
          size="x-small"
          variant="text"
        >
          <div v-if="!disableSelector" class="align-center d-flex" :class="labelClass">
            <v-progress-circular
              v-if="groupsLoading"
              indeterminate
              size="14"
              width="2"
            />
            <div class="ml-1">
              {{ label }}
            </div>
            <v-icon v-if="!groupsLoading" :icon="mdiMenuDown" size="24" />
          </div>
          <div v-if="isRemoving" :class="labelClass">
            <v-icon class="mr-1" :icon="mdiClose" />Removed
          </div>
          <div v-if="isAdding" :class="labelClass">
            <v-icon class="mr-1" :icon="mdiCheckBold" />Added
          </div>
        </v-btn>
      </template>
      <v-list
        v-if="!groupsLoading"
        density="compact"
        variant="flat"
      >
        <v-list-item v-if="!filter(useContextStore().currentUser.myCuratedGroups, ['domain', domain]).length" disabled>
          <span class="px-3 py-1 text-no-wrap">You have no {{ domainLabel(false) }}s.</span>
        </v-list-item>
        <v-list-item
          v-for="group in filter(useContextStore().currentUser.myCuratedGroups, ['domain', domain])"
          :key="group.id"
          density="compact"
          class="py-0"
          @click="groupCheckboxClick(group)"
          @keyup.enter="groupCheckboxClick(group)"
        >
          <v-checkbox
            :id="`${idFragment}-${group.id}-checkbox`"
            v-model="checkedGroups"
            :aria-label="includes(checkedGroups, group.id) ? `Remove ${student.name} from '${group.name}' group` : `Add ${student.name} to '${group.name}' group`"
            color="primary"
            density="compact"
            hide-details
            :value="group.id"
            @click="groupCheckboxClick(group)"
            @keyup.enter="groupCheckboxClick(group)"
          >
            <template #label>
              <div class="ml-2">
                <span class="sr-only">{{ domainLabel(true) }} </span>
                {{ group.name }}<span class="sr-only"> {{ checkedGroups.includes(group.id) ? 'is' : 'is not' }} selected</span>
              </div>
            </template>
          </v-checkbox>
        </v-list-item>
        <v-list-item class="align-center border-t-sm mt-2 pt-2" density="compact">
          <v-btn
            :id="`create-${idFragment}`"
            color="primary"
            :prepend-icon="mdiPlus"
            variant="text"
            @click="showModal = true"
          >
            Create New {{ domainLabel(true) }}
          </v-btn>
        </v-list-item>
      </v-list>
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
import {filter, includes, map, without} from 'lodash'
import {mdiCheckBold, mdiClose, mdiMenuDown, mdiPlus} from '@mdi/js'
import {useContextStore} from '@/stores/context'
</script>

<script>
import CreateCuratedGroupModal from '@/components/curated/CreateCuratedGroupModal'
import {
  addStudentsToCuratedGroup,
  createCuratedGroup,
  removeFromCuratedGroup
} from '@/api/curated'
import {alertScreenReader} from '@/lib/utils'
import {describeCuratedGroupDomain} from '@/berkeley'
import {putFocusNextTick} from '@/lib/utils'

export default {
  name: 'ManageStudent',
  components: {
    CreateCuratedGroupModal
  },
  props: {
    alignDropdownRight: {
      required: false,
      type: Boolean
    },
    domain: {
      required: true,
      type: String
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
    buttonColor() {
      return this.isAdding ? 'success' : (this.isRemoving ? 'red' : 'primary')
    },
    disableSelector() {
      return this.isAdding || this.isRemoving
    }
  },
  created() {
    this.idFragment = this.domainLabel(false).replace(' ', '-')
    this.dropdownId = `${this.idFragment}-dropdown-${this.student.sid}`
    this.refresh()
    useContextStore().setEventHandler('my-curated-groups-updated', this.onUpdateMyCuratedGroups)
  },
  unmounted() {
    useContextStore().removeEventHandler('my-curated-groups-updated', this.onUpdateMyCuratedGroups)
  },
  methods: {
    domainLabel(capitalize) {
      return describeCuratedGroupDomain(this.domain, capitalize)
    },
    groupCheckboxClick(group) {
      if (includes(this.checkedGroups, group.id)) {
        this.isRemoving = true
        const done = () => {
          this.checkedGroups = without(this.checkedGroups, group.id)
          this.isRemoving = false
          putFocusNextTick(this.dropdownId, 'button')
          alertScreenReader(`${this.student.name} removed from "${group.name}"`)
        }
        removeFromCuratedGroup(group.id, this.student.sid).finally(() =>
          setTimeout(done, this.confirmationTimeout)
        )
      } else {
        this.isAdding = true
        const done = () => {
          this.checkedGroups.push(group.id)
          this.isAdding = false
          putFocusNextTick(this.dropdownId, 'button')
          alertScreenReader(`${this.student.name} added to "${group.name}"`)
        }
        addStudentsToCuratedGroup(group.id, [this.student.sid]).finally(() => setTimeout(done, this.confirmationTimeout))
      }
    },
    onCreateCuratedGroup(name) {
      this.isAdding = true
      this.showModal = false
      const done = () => {
        putFocusNextTick(this.dropdownId, 'button')
        this.isAdding = false
      }
      createCuratedGroup(this.domain, name, [this.student.sid]).then(group => {
        this.checkedGroups.push(group.id)
        alertScreenReader(`${this.student.name} added to new ${this.domainLabel(false)}, "${name}".`)
        setTimeout(done, this.confirmationTimeout)
      })
    },
    onModalCancel() {
      this.showModal = false
      alertScreenReader('Canceled')
      putFocusNextTick(this.dropdownId, 'button')
    },
    onUpdateMyCuratedGroups(domain) {
      if (domain === this.domain) {
        this.refresh()
      }
    },
    refresh() {
      const containsSid = group => {
        return includes(group.sids, this.student.sid)
      }
      this.checkedGroups = map(filter(useContextStore().currentUser.myCuratedGroups, containsSid), 'id')
      this.groupsLoading = false
    }
  }
}
</script>

<style scoped>
.manage-student-btn {
  height: 24px;
  width: 8.5rem;
}
.opacity-zero {
  opacity: 0;
}
</style>
