<template>
  <div class="d-flex align-end">
    <label id="add-all-checkbox-label" :for="checkboxId" class="sr-only">
      Select all students on this page to add to a {{ domainLabel(false) }}
    </label>
    <div class="checkbox-container" :class="{'checked-checkbox-container': size(sids)}">
      <input
        :id="checkboxId"
        v-model="isSelectAllChecked"
        :aria-controls="`add-to-${idFragment}`"
        class="checkbox"
        :disabled="isSaving"
        :indeterminate="indeterminate"
        type="checkbox"
        @update:model-value="toggle"
      />
    </div>
    <div class="button-container">
      <v-menu
        :id="dropdownId"
        :close-on-content-click="false"
        :disabled="!size(sids) || isConfirming || isSaving"
        @update:model-value="isOpen => isMenuOpen = isOpen"
      >
        <template #activator="{props: menuProps}">
          <button
            :id="`add-to-${idFragment}`"
            class="button-menu bg-primary py-0 px-2 text-body-1 text-white"
            :class="{'bg-success': isConfirming, 'button-menu-active': isMenuOpen}"
            :disabled="!size(sids)"
            v-bind="menuProps"
          >
            <div class="align-center d-flex">
              <v-progress-circular
                v-if="isSaving && !isConfirming"
                indeterminate
                size="14"
                width="2"
              />
              <div v-if="!isConfirming" class="ml-1">
                {{ isSaving ? 'Adding' : 'Add' }} <span class="sr-only">{{ pluralize('selected student', size(sids)) }}</span> to {{ domainLabel(true) }}
              </div>
              <v-icon v-if="!isSaving && !isConfirming" :icon="mdiMenuDown" />
              <div v-if="isConfirming" class="align-center d-flex">
                <v-icon class="mr-1" :icon="mdiCheckBold" size="14" /><span>Added to {{ domainLabel(true) }}</span>
              </div>
            </div>
          </button>
        </template>
        <v-list
          v-model:selected="selectedCuratedGroups"
          :aria-label="`Select one or more ${domainLabel(true)}s`"
          class="overflow-x-hidden"
          density="compact"
          select-strategy="leaf"
          variant="flat"
        >
          <v-list-item v-if="!size(myCuratedGroups)" disabled>
            <span class="px-3 py-1 text-no-wrap">You have no {{ domainLabel(false) }}s.</span>
          </v-list-item>
          <v-list-item
            v-for="group in myCuratedGroups"
            :key="group.id"
            :aria-checked="!!find(selectedCuratedGroups, {'id': group.id})"
            class="v-list-item-override py-0"
            density="compact"
            role="checkbox"
            :value="group"
          >
            <template #prepend="{isSelected}">
              <v-list-item-action start>
                <v-checkbox-btn
                  :id="`${idFragment}-${group.id}-checkbox`"
                  :model-value="isSelected"
                  class="mr-7 w-100"
                  color="primary"
                  density="compact"
                  hide-details
                  role="presentation"
                  tabindex="-1"
                >
                  <template #label>
                    <span class="truncate-with-ellipsis ml-2">
                      {{ group.name }}
                    </span>
                  </template>
                </v-checkbox-btn>
              </v-list-item-action>
            </template>
          </v-list-item>
          <v-list-item>
            <v-btn
              :id="`submit-${idFragment}`"
              :aria-label="`Add students to selected ${domainLabel(true)}s`"
              class="px-6"
              color="primary"
              :disabled="!size(selectedCuratedGroups) || isConfirming || isSaving"
              height="32"
              text="Add"
              @click.stop="onSubmit"
              @keydown.enter.stop="onSubmit"
            />
          </v-list-item>
          <v-list-item class="border-t-sm mt-2 pt-2 px-1" density="compact">
            <v-btn
              :id="`create-${idFragment}`"
              :aria-label="`Create a new ${domainLabel(false)}`"
              color="primary"
              :prepend-icon="mdiPlus"
              :text="`Create New ${domainLabel(true)}`"
              slim
              variant="text"
              @click.stop="showModal = true"
              @keydown.enter.stop="showModal = true"
            />
          </v-list-item>
        </v-list>
      </v-menu>
    </div>
    <CreateCuratedGroupModal
      :cancel="modalCancel"
      :create="modalCreateCuratedGroup"
      :domain="domain"
      :show-modal="showModal"
    />
  </div>
</template>

<script setup>
import {computed, onMounted, onUnmounted, reactive, ref} from 'vue'
import {filter as _filter, each, find, inRange, map, remove, size} from 'lodash'
import {mdiCheckBold, mdiMenuDown, mdiPlus} from '@mdi/js'
import CreateCuratedGroupModal from '@/components/curated/CreateCuratedGroupModal'
import {addStudentsToCuratedGroups, createCuratedGroup} from '@/api/curated'
import {alertScreenReader, oxfordJoin, pluralize, putFocusNextTick} from '@/lib/utils'
import {describeCuratedGroupDomain} from '@/lib/berkeley-utils'
import {useContextStore} from '@/stores/context'

const props = defineProps({
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
})

const contextStore = useContextStore()

const idFragment = describeCuratedGroupDomain(props.domain, false).replace(' ', '-')
const checkboxId = `add-all-to-${idFragment}`
const currentUser = reactive(contextStore.currentUser)
const dropdownId = `${idFragment}-dropdown-select`
const indeterminate = ref(false)
const isConfirming = ref(false)
const isMenuOpen = ref(false)
const isSaving = ref(false)
const isSelectAllChecked = ref(false)
const selectedCuratedGroups = ref([])
const showModal = ref(false)
const sids = ref([])

const myCuratedGroups = computed(() => {
  return _filter(currentUser.myCuratedGroups, ['domain', props.domain])
})

onMounted(() => {
  contextStore.setEventHandler('curated-group-checkbox-checked', onCheckboxChecked)
  contextStore.setEventHandler('curated-group-checkbox-unchecked', onCheckboxUnchecked)
  contextStore.setEventHandler('curated-group-deselect-all', () => {
    isSelectAllChecked.value = indeterminate.value = false
  })
})

onUnmounted(() => {
  each(['curated-group-checkbox-checked', 'curated-group-checkbox-unchecked', 'curated-group-deselect-all'], contextStore.removeEventHandler)
})

const afterCreateGroup = () => {
  sids.value = []
  refresh()
  toggle(false)
  putFocusNextTick(checkboxId)
  props.onCreateCuratedGroup()
}

const domainLabel = capitalize => {
  return describeCuratedGroupDomain(props.domain, capitalize)
}

const modalCancel = () => {
  alertScreenReader('Canceled')
  showModal.value = false
  putFocusNextTick(isMenuOpen.value ? `create-${idFragment}` : checkboxId)
}

const modalCreateCuratedGroup = name => {
  isSaving.value = true
  showModal.value = false
  alertScreenReader(`Adding ${pluralize('student', size(sids.value))} to new ${domainLabel(false)}.`)
  return createCuratedGroup(props.domain, name, sids.value).then(() => {
    isSaving.value = false
    isConfirming.value = true
    alertScreenReader(`${pluralize('student', size(sids.value))} added to ${domainLabel(false)} ${name}`)
  }).finally(() => {
    setTimeout(
      () => {
        afterCreateGroup()
        isConfirming.value = false
      },
      2000
    )
  })
}

const onCheckboxChecked = args => {
  if (props.domain === args.domain) {
    sids.value.push(args.sid)
    refresh()
  }
}

const onCheckboxUnchecked = args => {
  if (props.domain === args.domain) {
    sids.value = remove(sids.value, s => s !== args.sid)
    refresh()
  }
}

const onSubmit = () => {
  isSaving.value = true
  const groupCount = size(selectedCuratedGroups.value)
  const groupDescription = groupCount > 1 ? pluralize(domainLabel(false), groupCount) : domainLabel(false)
  const groupIds = map(selectedCuratedGroups.value, 'id')
  const groupNames = oxfordJoin(map(selectedCuratedGroups.value, 'name'))
  const studentCount = pluralize('student', size(sids.value))
  alertScreenReader(`Adding ${studentCount} to ${groupDescription}`)
  addStudentsToCuratedGroups(groupIds, sids.value).then(() => {
    isSaving.value = false
    isConfirming.value = true
  }).finally(() => {
    setTimeout(
      () => {
        isConfirming.value = false
        isSelectAllChecked.value = indeterminate.value = false
        selectedCuratedGroups.value = []
        contextStore.broadcast('curated-group-deselect-all', props.domain)
        alertScreenReader(`${studentCount} added to ${groupDescription} ${groupNames}.`)
        sids.value = []
        putFocusNextTick(checkboxId)
      },
      2000
    )
  })
}

const refresh = () => {
  indeterminate.value = inRange(size(sids.value), 1, size(props.students))
  isSelectAllChecked.value = size(sids.value) === size(props.students)
}

const toggle = checked => {
  sids.value = []
  if (checked) {
    each(props.students, student => {
      sids.value.push(student.sid || student.csEmplId)
    })
    contextStore.broadcast('curated-group-select-all', props.domain)
    alertScreenReader(`Use the "Add selected students to ${domainLabel(true)}" button menu to choose ${domainLabel(true)}s`)
  } else {
    contextStore.broadcast('curated-group-deselect-all', props.domain)
  }
}
</script>

<style scoped>
.button-container {
  min-width: 15rem;
}</style>
