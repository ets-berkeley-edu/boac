<template>
  <div :class="{'opacity-zero': srOnly && !isAdding && !isRemoving && !showModal}">
    <v-menu
      :aria-label="`${domainLabel(true)}s for ${student.name}`"
      :close-on-content-click="false"
      :disabled="isAdding || isRemoving"
      @update:model-value="onUpdateMenuModelValue"
    >
      <template #activator="{props: menuProps}">
        <button
          :id="menuButtonId"
          v-bind="menuProps"
          :aria-label="`Add ${student.name} to ${domainLabel(true)}s`"
          class="button-menu bg-primary py-0 px-2 text-body-1 text-white"
          :class="{
            'bg-error': isRemoving,
            'bg-success': isAdding,
            'button-menu-active': isMenuOpen
          }"
        >
          <div v-if="!isAdding && !isRemoving" class="d-flex" :class="labelClass">
            <v-progress-circular
              v-if="groupsLoading"
              indeterminate
              size="14"
              width="2"
            />
            <div class="ml-1">
              {{ label }}
            </div>
            <v-icon v-if="!isRemoving && !isAdding" :icon="mdiMenuDown" />
          </div>
          <div v-if="isRemoving && !isAdding" class="align-center d-flex" :class="labelClass">
            <v-icon class="mr-1" :icon="mdiCloseThick" />
            <div>
              Removed
            </div>
          </div>
          <div v-if="isAdding && !isRemoving" class="align-center d-flex" :class="labelClass">
            <v-icon class="mr-1" :icon="mdiCheckBold" />
            <div>
              Added
            </div>
          </div>
          <div v-if="isRemoving && isAdding" class="align-center d-flex" :class="labelClass">
            <v-icon class="mr-1" :icon="mdiCheckBold" />
            <div>
              Updated
            </div>
          </div>
        </button>
      </template>
      <v-list
        v-model:selected="selectedGroupIds"
        :aria-label="`${props.student.name}\'s ${domainLabel(true)} memberships`"
        class="overflow-x-hidden"
        density="compact"
        select-strategy="leaf"
        variant="flat"
      >
        <v-list-item v-if="!size(filteredCuratedGroups)" disabled>
          <span class="px-3 py-1 text-no-wrap">You have no {{ domainLabel(false) }}s.</span>
        </v-list-item>
        <v-list-item
          v-for="group in filteredCuratedGroups"
          :key="group.id"
          :aria-checked="!!includes(selectedGroupIds, group.id)"
          density="compact"
          class="v-list-item-override py-0"
          role="checkbox"
          :value="group.id"
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
            :aria-label="`Apply changes to ${student.name}'s ${domainLabel(true)} memberships`"
            class="px-6"
            color="primary"
            :disabled="!size(xor(existingGroupMemberships, selectedGroupIds)) || isAdding || isRemoving"
            height="32"
            text="Apply"
            @click.stop="onSubmit"
            @keydown.enter.stop="onSubmit"
          />
        </v-list-item>
        <v-list-item class="align-center border-t-sm mt-2 pt-2 px-1" density="compact">
          <v-btn
            :id="`create-${idFragment}`"
            color="primary"
            :prepend-icon="mdiPlus"
            slim
            variant="text"
            @click.stop="showModal = true"
            @keydown.enter.stop="showModal = true"
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
import CreateCuratedGroupModal from '@/components/curated/CreateCuratedGroupModal'
import {
  addStudentsToCuratedGroups,
  createCuratedGroup,
  removeFromCuratedGroups
} from '@/api/curated'
import {alertScreenReader} from '@/lib/utils'
import {computed, onMounted, onUnmounted, ref} from 'vue'
import {describeCuratedGroupDomain} from '@/berkeley'
import {filter as _filter, clone, difference, includes, map, noop, size, xor} from 'lodash'
import {getUserProfile} from '@/api/user'
import {mdiCheckBold, mdiCloseThick, mdiMenuDown, mdiPlus} from '@mdi/js'
import {pluralize, putFocusNextTick} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  buttonWidth: {
    default: undefined,
    required: false,
    type: [Number, String]
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
})

const contextStore = useContextStore()

const selectedGroupIds = ref(undefined)
const confirmationTimeout = ref(1500)
const currentUser = contextStore.currentUser
const eventName = 'my-curated-groups-updated'
const groupsLoading = ref(true)
const idFragment = describeCuratedGroupDomain(props.domain).replace(' ', '-')
const isAdding = ref(false)
const isMenuOpen = ref(false)
const isRemoving = ref(false)
const menuButtonId = `student-${props.student.sid}-add-to-${idFragment}`
const showModal = ref(false)

const existingGroupMemberships = computed(() => {
  const containsSid = group => {
    return includes(group.sids, props.student.sid)
  }
  return map(_filter(contextStore.currentUser.myCuratedGroups, containsSid), 'id')
})

const filteredCuratedGroups = computed(() => {
  return _filter(currentUser.myCuratedGroups, ['domain', props.domain])
})

onMounted(() => {
  refresh()
  contextStore.setEventHandler(eventName, onUpdateMyCuratedGroups)
})

onUnmounted(() => {
  contextStore.removeEventHandler(eventName, onUpdateMyCuratedGroups)
})

const domainLabel = capitalize => {
  return describeCuratedGroupDomain(props.domain, capitalize)
}

const onCreateCuratedGroup = name => {
  isAdding.value = true
  showModal.value = false
  putFocusNextTick(menuButtonId)
  const done = () => {
    isAdding.value = false
  }
  alertScreenReader(`Adding student to new ${domainLabel(false)}.`)
  return createCuratedGroup(props.domain, name, [props.student.sid]).then(group => {
    selectedGroupIds.value.push(group.id)
    alertScreenReader(`${props.student.name} added to new ${domainLabel(false)}, "${name}".`)
    setTimeout(done, confirmationTimeout.value)
  })
}

const onModalCancel = () => {
  alertScreenReader('Canceled')
  showModal.value = false
  putFocusNextTick(isMenuOpen.value ? `create-${idFragment}` : menuButtonId)
}

const onSubmit = () => {
  const addToGroups = difference(selectedGroupIds.value, existingGroupMemberships.value)
  const removeFromGroups = difference(existingGroupMemberships.value, selectedGroupIds.value)
  const actions = []
  let alert = `${props.student.name}`
  alertScreenReader('Applying changes.')
  putFocusNextTick(menuButtonId)
  if (size(addToGroups)) {
    const groupCount = size(addToGroups)
    const groupDescription = groupCount > 1 ? pluralize(domainLabel(false), groupCount) : domainLabel(false)
    actions.push(new Promise(resolve => {
      isAdding.value = true
      addStudentsToCuratedGroups(addToGroups, [props.student.sid]).then(resolve)
    }))
    alert = alert.concat(` added to ${groupDescription}`)
  }
  if (size(removeFromGroups)) {
    const groupCount = size(removeFromGroups)
    const groupDescription = groupCount > 1 ? pluralize(domainLabel(false), groupCount) : domainLabel(false)
    actions.push(new Promise(resolve => {
      isRemoving.value = true
      removeFromCuratedGroups(removeFromGroups, props.student.sid).then(noop)
      resolve()
    }))
    alert = alert.concat(`${size(addToGroups) ? ' and' : ''} removed from ${groupDescription}`)
  }
  const done = () => {
    if (isAdding.value || isRemoving.value) {
      alertScreenReader(alert)
    }
    contextStore.broadcast('curated-group-deselect-all', props.domain)
    isAdding.value = isRemoving.value = false
    // Changes in curated-group may impact cohort counts thus we refresh user-session object.
    getUserProfile().then(contextStore.setCurrentUser)
  }
  Promise.all(actions).finally(() => setTimeout(done, confirmationTimeout.value))
}

const onUpdateMenuModelValue = isOpen => {
  isMenuOpen.value = isOpen
  refresh()
  if (!isMenuOpen.value) {
    contextStore.broadcast('curated-group-deselect-all', props.domain)
  }
}
const onUpdateMyCuratedGroups = domain => {
  if (domain === props.domain) {
    refresh()
  }
}

const refresh = () => {
  selectedGroupIds.value = clone(existingGroupMemberships.value)
  groupsLoading.value = false
}
</script>

<style scoped>
.button-menu {
  width: v-bind(buttonWidth);
}
.opacity-zero {
  opacity: 0;
}
</style>
