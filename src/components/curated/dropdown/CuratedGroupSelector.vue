<template>
  <div class="add-to-curated-group-container d-flex align-end">
    <label id="add-all-checkbox-label" :for="checkboxId" class="sr-only">
      Select all students to add to a {{ domainLabel(false) }}
    </label>
    <div class="select-all-checkbox-container">
      <div class="select-all-checkbox-layer" />
      <div class="select-all-checkbox-layer">
        <v-checkbox-btn
          :id="checkboxId"
          v-model="isSelectAllChecked"
          :aria-controls="dropdownId"
          base-color="primary"
          class="select-all-checkbox"
          color="primary"
          density="comfortable"
          :disabled="isSaving"
          hide-details
          :indeterminate="indeterminate"
          @update:model-value="toggle"
        />
      </div>
    </div>
    <v-menu
      v-if="!!size(sids)"
      :id="dropdownId"
      :disabled="isConfirming || isSaving"
    >
      <template #activator="{props}">
        <v-btn
          :id="isSaving ? `add-to-${idFragment}-confirmation` : `add-to-${idFragment}`"
          :color="isConfirming ? 'success' : 'primary'"
          slim
          variant="flat"
          v-bind="props"
        >
          <div class="align-center d-flex">
            <v-progress-circular
              v-if="isSaving && !isConfirming"
              indeterminate
              size="14"
              width="2"
            />
            <div v-if="!isConfirming" class="ml-1">
              {{ isSaving ? 'Adding' : 'Add' }} to {{ domainLabel(true) }}
            </div>
            <v-icon v-if="!isSaving && !isConfirming" :icon="mdiMenuDown" />
            <div v-if="isConfirming" class="align-center d-flex">
              <v-icon class="mr-1" :icon="mdiCheckBold" size="14" /><span>Added to {{ domainLabel(true) }}</span>
            </div>
          </div>
        </v-btn>
      </template>
      <v-card density="compact">
        <v-list density="compact" variant="flat">
          <v-list-item v-if="!size(myCuratedGroups)">
            <span class="text-grey px-3 py-1 text-no-wrap">You have no {{ domainLabel(false) }}s.</span>
          </v-list-item>
          <v-list-item
            v-for="group in myCuratedGroups"
            :key="group.id"
            density="compact"
            @click="curatedGroupCheckboxClick(group)"
          >
            <template #prepend>
              <v-checkbox
                :id="`${idFragment}-${group.id}-checkbox`"
                class="mr-2"
                density="compact"
                hide-details
                @click="curatedGroupCheckboxClick(group)"
                @keyup.enter="curatedGroupCheckboxClick(group)"
              >
                <template #label>
                  <span class="ml-2">
                    {{ group.name }}
                  </span>
                </template>
              </v-checkbox>
            </template>
          </v-list-item>
          <v-list-item class="border-t-sm mt-2 pt-2" density="compact">
            <v-btn
              :id="`create-${idFragment}`"
              :aria-label="`Create a new ${domainLabel(false)}`"
              color="primary"
              :prepend-icon="mdiPlus"
              :text="`Create New ${domainLabel(true)}`"
              variant="text"
              @click="showModal = true"
            />
          </v-list-item>
        </v-list>
      </v-card>
    </v-menu>
    <CreateCuratedGroupModal
      :cancel="modalCancel"
      :create="modalCreateCuratedGroup"
      :domain="domain"
      :show-modal="showModal"
    />
  </div>
</template>

<script setup>
import {each, filter, inRange, remove, size} from 'lodash'
import {mdiCheckBold, mdiMenuDown, mdiPlus} from '@mdi/js'
import {putFocusNextTick} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
</script>

<script>
import CreateCuratedGroupModal from '@/components/curated/CreateCuratedGroupModal'
import {addStudentsToCuratedGroup, createCuratedGroup} from '@/api/curated'
import {describeCuratedGroupDomain} from '@/berkeley'

export default {
  name: 'CuratedGroupSelector',
  components: {CreateCuratedGroupModal},
  props: {
    contextDescription: {
      required: true,
      type: String
    },
    domain: {
      required: true,
      type: String
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
    idFragment: undefined,
    indeterminate: false,
    isConfirming: false,
    isSaving: false,
    isSelectAllChecked: false,
    showModal: false,
    sids: []
  }),
  computed: {
    myCuratedGroups() {
      return filter(useContextStore().currentUser.myCuratedGroups, ['domain', this.domain])
    }
  },
  created() {
    this.idFragment = this.domainLabel(false).replace(' ', '-')
    this.checkboxId = `add-all-to-${this.idFragment}`
    this.dropdownId = `${this.idFragment}-dropdown-select`
    useContextStore().setEventHandler('curated-group-checkbox-checked', this.onCheckboxChecked)
    useContextStore().setEventHandler('curated-group-checkbox-unchecked', this.onCheckboxUnchecked)
  },
  unmounted() {
    useContextStore().removeEventHandler('curated-group-checkbox-checked', this.onCheckboxChecked)
    useContextStore().removeEventHandler('curated-group-checkbox-unchecked', this.onCheckboxUnchecked)
  },
  methods: {
    afterAddStudents(group) {
      useContextStore().alertScreenReader(`${size(this.sids)} student${size(this.sids) === 1 ? '' : 's'} added to ${this.domainLabel(true)} "${group.name}".`)
      this.sids = []
      this.isSelectAllChecked = this.indeterminate = false
      useContextStore().broadcast('curated-group-deselect-all', this.domain)
    },
    afterCreateGroup() {
      this.sids = []
      this.refresh()
      this.toggle(false)
      putFocusNextTick(this.checkboxId)
      this.onCreateCuratedGroup()
    },
    afterCreateGroupModalCancel() {
      this.sids = []
      this.refresh()
      this.toggle(false)
      putFocusNextTick(this.checkboxId)
    },
    curatedGroupCheckboxClick(group) {
      this.isSaving = true
      addStudentsToCuratedGroup(group.id, this.sids).then(() => {
        this.isSaving = false
        this.isConfirming = true
      }).finally(() => {
        setTimeout(
          () => {
            this.isConfirming = false
            this.afterAddStudents(group)
            useContextStore().alertScreenReader(`Student${size(this.sids) === 1 ? 's' : ''} added to ${this.domainLabel(false)} ${group.name}`)
          },
          2000
        )
      })
    },
    domainLabel(capitalize) {
      return describeCuratedGroupDomain(this.domain, capitalize)
    },
    refresh() {
      this.indeterminate = inRange(size(this.sids), 1, size(this.students))
      this.isSelectAllChecked = size(this.sids) === size(this.students)
    },
    modalCancel() {
      this.showModal = false
      useContextStore().alertScreenReader('Canceled')
    },
    modalCreateCuratedGroup(name) {
      this.isSaving = true
      return createCuratedGroup(this.domain, name, this.sids).then(() => {
        this.showModal = false
        this.isSaving = false
        this.isConfirming = true
        useContextStore().alertScreenReader(`Student${size(this.sids) === 1 ? 's' : ''} added to ${this.domainLabel(false)} ${name}`)
      }).finally(() => {
        setTimeout(
          () => {
            this.afterCreateGroup()
            this.isConfirming = false
          },
          2000
        )
      })
    },
    onCheckboxChecked(args) {
      if (this.domain === args.domain) {
        this.sids.push(args.sid)
        this.refresh()
      }
    },
    onCheckboxUnchecked(args) {
      if (this.domain === args.domain) {
        this.sids = remove(this.sids, s => s !== args.sid)
        this.refresh()
      }
    },
    toggle(checked) {
      this.sids = []
      if (checked) {
        each(this.students, student => {
          this.sids.push(student.sid || student.csEmplId)
        })
        useContextStore().broadcast('curated-group-select-all', this.domain)
        putFocusNextTick(this.dropdownId, 'button')
        useContextStore().alertScreenReader('All students on this page selected.')
      } else {
        useContextStore().broadcast('curated-group-deselect-all', this.domain)
        useContextStore().alertScreenReader('All students on this page deselected.')
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
.add-to-curated-group-container {
  min-width: 270px;
  padding-bottom: 9px;
}
.select-all-checkbox {
  z-index: 100;
}
.select-all-checkbox-container {
  background-color: #eee;
  border: 1px solid #aaa;
  border-radius: 36px;
  height: 36px;
  margin-right: 8px;
  position: relative;
  width: 36px;
}
.select-all-checkbox-layer {
  bottom: 1px;
  height: 100%;
  position: absolute;
  right: 1px;
  width: 100%;
}
</style>
