<template>
  <div :class="{'opacity-zero': srOnly && !isAdding && !isRemoving && !showModal}">
    <v-menu
      :aria-label="`${domainLabel(true)}s for ${student.name}`"
      :disabled="isAdding || isRemoving"
    >
      <template #activator="{props: menuProps}">
        <v-btn
          :id="menuButtonId"
          v-bind="menuProps"
          :append-icon="(buttonVariant && !groupsLoading && !isAdding && !isRemoving) ? mdiMenuDown : undefined"
          :aria-label="`Add ${student.name} to a curated group`"
          :color="isAdding ? 'success' : (isRemoving ? 'error' : 'primary')"
          :variant="buttonVariant"
          :width="buttonWidth"
        >
          <div v-if="!isAdding && !isRemoving" :class="labelClass">
            <v-progress-circular
              v-if="groupsLoading"
              indeterminate
              size="14"
              width="2"
            />
            <div class="ml-1">
              {{ label }}
            </div>
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
        </v-btn>
      </template>
      <v-list
        v-if="!groupsLoading"
        density="compact"
        max-width="90%"
        variant="flat"
      >
        <v-list-item v-if="!_filter(currentUser.myCuratedGroups, ['domain', domain]).length" disabled>
          <span class="px-3 py-1 text-no-wrap">You have no {{ domainLabel(false) }}s.</span>
        </v-list-item>
        <v-list-item
          v-for="group in _filter(currentUser.myCuratedGroups, ['domain', domain])"
          :key="group.id"
          density="compact"
          class="v-list-item-override py-0"
          @click.stop="onClickCuratedGroup(group)"
          @keyup.enter="onClickCuratedGroup(group)"
        >
          <v-checkbox
            :id="`${idFragment}-${group.id}-checkbox`"
            v-model="checkedGroups"
            :aria-label="includes(checkedGroups, group.id) ? `Remove ${student.name} from '${group.name}' group` : `Add ${student.name} to '${group.name}' group`"
            class="mr-7 w-100"
            color="primary"
            density="compact"
            hide-details
            :value="group.id"
          >
            <template #label>
              <div class="truncate-with-ellipsis ml-2">
                <span class="sr-only">{{ domainLabel(true) }} </span>
                {{ group.name }}<span class="sr-only"> {{ checkedGroups.includes(group.id) ? 'is' : 'is not' }} selected</span>
              </div>
            </template>
          </v-checkbox>
        </v-list-item>
        <v-list-item>
          <v-btn
            :id="`submit-${idFragment}`"
            :aria-label="`Apply changes to ${student.name}'s ${domainLabel(true)} memberhips`"
            class="px-6"
            color="primary"
            :disabled="!size(xor(existingGroupMemberships, checkedGroups)) || isAdding || isRemoving"
            height="32"
            text="Apply"
            @click="onSubmit"
          />
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
import CreateCuratedGroupModal from '@/components/curated/CreateCuratedGroupModal'
import {
  addStudentsToCuratedGroups,
  createCuratedGroup,
  removeFromCuratedGroups
} from '@/api/curated'
import {alertScreenReader} from '@/lib/utils'
import {describeCuratedGroupDomain} from '@/berkeley'
import {clone, difference, filter as _filter, includes, map, size, xor} from 'lodash'
import {mdiCheckBold, mdiCloseThick, mdiMenuDown, mdiPlus} from '@mdi/js'
import {pluralize, putFocusNextTick} from '@/lib/utils'
import {computed, onMounted, onUnmounted, ref} from 'vue'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  buttonVariant: {
    default: 'text',
    required: false,
    type: String
  },
  buttonWidth: {
    default: 136,
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

const checkedGroups = ref(undefined)
const confirmationTimeout = ref(1500)
const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const eventName = 'my-curated-groups-updated'
const groupsLoading = ref(true)
const idFragment = describeCuratedGroupDomain(props.domain).replace(' ', '-')
const isAdding = ref(false)
const isRemoving = ref(false)
const showModal = ref(false)

const existingGroupMemberships = computed(() => {
  const containsSid = group => {
    return includes(group.sids, props.student.sid)
  }
  return map(_filter(contextStore.currentUser.myCuratedGroups, containsSid), 'id')
})

const menuButtonId = computed(() => {
  return `student-${props.student.sid}-${isAdding.value ? `added-to-${idFragment}` : (isRemoving.value ? `removed-from-${idFragment}` : `add-to-${idFragment}`)}`
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

const onClickCuratedGroup = group => {
  const selected = checkedGroups.value.findIndex(id => id === group.id)
  if (selected >= 0) {
    checkedGroups.value.splice(selected, 1)
  } else {
    checkedGroups.value.push(group.id)
  }
}

const onCreateCuratedGroup = name => {
  isAdding.value = true
  showModal.value = false
  const done = () => {
    putFocusNextTick(menuButtonId.value)
    isAdding.value = false
  }
  return createCuratedGroup(props.domain, name, [props.student.sid]).then(group => {
    checkedGroups.value.push(group.id)
    alertScreenReader(`${props.student.name} added to new ${domainLabel(false)}, "${name}".`)
    setTimeout(done, confirmationTimeout.value)
  })
}

const onModalCancel = () => {
  showModal.value = false
  alertScreenReader('Canceled')
  putFocusNextTick(menuButtonId.value)
}

const onSubmit = () => {
  const addToGroups = difference(checkedGroups.value, existingGroupMemberships.value)
  const removeFromGroups = difference(existingGroupMemberships.value, checkedGroups.value)
  let actions = []
  let alert = `${props.student.name}`
  if (size(addToGroups)) {
    const groupCount = size(addToGroups)
    const groupDescription = groupCount > 1 ? pluralize(domainLabel(false), groupCount) : domainLabel(false)
    actions.push(new Promise(resolve => {
      isAdding.value = true
      addStudentsToCuratedGroups(addToGroups, [props.student.sid]).then(resolve)
    }))
    alert.concat(` added to ${groupDescription}`)
  }
  if (size(removeFromGroups)) {
    const groupCount = size(removeFromGroups)
    const groupDescription = groupCount > 1 ? pluralize(domainLabel(false), groupCount) : domainLabel(false)
    actions.push(new Promise(resolve => {
      isRemoving.value = true
      removeFromCuratedGroups(removeFromGroups, props.student.sid).then(resolve)
    }))
    alert.concat(`${size(addToGroups) ? ' and' : ''} removed from ${groupDescription}`)
  }
  const done = () => {
    isAdding.value = isRemoving.value = false
    putFocusNextTick(menuButtonId.value)
    alertScreenReader(alert)
  }
  Promise.all(actions).finally(() => setTimeout(done, confirmationTimeout.value))
}

const onUpdateMyCuratedGroups = domain => {
  if (domain === props.domain) {
    refresh()
  }
}

const refresh = () => {
  checkedGroups.value = clone(existingGroupMemberships.value)
  groupsLoading.value = false
}
</script>

<style scoped>
.opacity-zero {
  opacity: 0;
}
</style>
