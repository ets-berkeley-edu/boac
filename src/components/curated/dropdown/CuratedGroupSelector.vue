<template>
  <div class="align-center d-flex">
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
      v-if="!!_size(sids)"
      :id="dropdownId"
      :disabled="isConfirming || isSaving"
    >
      <template #activator="{props}">
        <v-btn
          :id="isSaving ? `add-to-${idFragment}-confirmation` : `add-to-${idFragment}`"
          :color="isConfirming || isSaving ? 'success' : 'primary'"
          variant="flat"
          v-bind="props"
        >
          <div class="align-center d-flex">
            <div v-if="!isConfirming" class="pr-2">
              {{ isSaving ? 'Adding' : 'Add' }} to {{ domainLabel(true) }}
            </div>
            <v-progress-circular
              v-if="isSaving"
              indeterminate
              size="14"
              width="2"
            />
            <v-icon v-if="!isSaving" :icon="mdiMenuDown" />
            <div v-if="isConfirming">
              <v-icon :icon="mdiCheckBold" /> Added to {{ domainLabel(true) }}
            </div>
          </div>
        </v-btn>
      </template>
      <v-card density="compact">
        <v-list density="compact" variant="flat">
          <v-list-item v-if="!myCuratedGroups.length">
            <span class="text-no-wrap pb-1 pl-3 pr-3 pt-1 faint-text">You have no {{ domainLabel(false) }}s.</span>
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
    <v-dialog
      v-model="showModal"
      body-class="pl-0 pr-0"
      hide-footer
      hide-header
      @shown="putFocusNextTick('modal-header')"
    >
      <CreateCuratedGroupModal
        :cancel="modalCancel"
        :create="modalCreateCuratedGroup"
        :domain="domain"
      />
    </v-dialog>
  </div>
</template>

<script setup>
import {mdiCheckBold, mdiMenuDown, mdiPlus} from '@mdi/js'
</script>

<script>
import CreateCuratedGroupModal from '@/components/curated/CreateCuratedGroupModal'
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import {addStudentsToCuratedGroup, createCuratedGroup} from '@/api/curated'
import {describeCuratedGroupDomain} from '@/berkeley'

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
      return this._filter(this.currentUser.myCuratedGroups, ['domain', this.domain])
    }
  },
  created() {
    this.idFragment = this.domainLabel(false).replace(' ', '-')
    this.checkboxId = `add-all-to-${this.idFragment}`
    this.dropdownId = `${this.idFragment}-dropdown-select`
    this.setEventHandler('curated-group-checkbox-checked', this.onCheckboxChecked)
    this.setEventHandler('curated-group-checkbox-unchecked', this.onCheckboxUnchecked)
  },
  unmounted() {
    this.removeEventHandler('curated-group-checkbox-checked', this.onCheckboxChecked)
    this.removeEventHandler('curated-group-checkbox-unchecked', this.onCheckboxUnchecked)
  },
  methods: {
    afterAddStudents(group) {
      this.alertScreenReader(`${this.sids.length} student${this.sids.length === 1 ? '' : 's'} added to ${this.domainLabel(true)} "${group.name}".`)
      this.sids = []
      this.isSelectAllChecked = this.indeterminate = false
      this.broadcast('curated-group-deselect-all', this.domain)
    },
    afterCreateGroup() {
      this.sids = []
      this.refresh()
      this.toggle(false)
      this.putFocusNextTick(this.checkboxId)
      this.onCreateCuratedGroup()
    },
    afterCreateGroupModalCancel() {
      this.sids = []
      this.refresh()
      this.toggle(false)
      this.putFocusNextTick(this.checkboxId)
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
            this.alertScreenReader(`Student${this.sids.length === 1 ? 's' : ''} added to ${this.domainLabel(false)} ${group.name}`)
          },
          2000
        )
      })
    },
    domainLabel(capitalize) {
      return describeCuratedGroupDomain(this.domain, capitalize)
    },
    refresh() {
      this.indeterminate = this._inRange(this._size(this.sids), 1, this._size(this.students))
      this.isSelectAllChecked = this._size(this.sids) === this._size(this.students)
    },
    modalCancel() {
      this.showModal = false
      this.alertScreenReader('Canceled')
    },
    modalCreateCuratedGroup(name) {
      this.isSaving = true
      this.showModal = false
      createCuratedGroup(this.domain, name, this.sids).then(() => {
        this.isSaving = false
        this.isConfirming = true
      }).finally(() => {
        setTimeout(
          () => {
            this.afterCreateGroup()
            this.isConfirming = false
            this.alertScreenReader(`Student${this.sids.length === 1 ? 's' : ''} added to ${this.domainLabel(false)} ${name}`)
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
        this.sids = this._remove(this.sids, s => s !== args.sid)
        this.refresh()
      }
    },
    toggle(checked) {
      this.sids = []
      if (checked) {
        this._each(this.students, student => {
          this.sids.push(student.sid || student.csEmplId)
        })
        this.broadcast('curated-group-select-all', this.domain)
        this.putFocusNextTick(this.dropdownId, 'button')
        this.alertScreenReader('All students on this page selected.')
      } else {
        this.broadcast('curated-group-deselect-all', this.domain)
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
