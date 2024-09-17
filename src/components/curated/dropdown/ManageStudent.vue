<template>
  <div :class="{'opacity-zero': srOnly && !isAdding && !isRemoving && !showModal}">
    <v-menu
      :aria-label="`${domainLabel(true)}s for ${student.name}`"
      :disabled="isAdding || isRemoving"
    >
      <template #activator="{props}">
        <v-btn
          :id="menuButtonId"
          v-bind="props"
          :append-icon="(buttonVariant && !groupsLoading && !isAdding && !isRemoving) ? mdiMenuDown : undefined"
          :aria-label="`Add ${student.name} to a curated group`"
          :color="isAdding ? 'success' : (isRemoving ? 'error' : 'primary')"
          :variant="buttonVariant"
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
          <div v-if="isRemoving" class="align-center d-flex" :class="labelClass">
            <v-icon class="mr-1" :icon="mdiCloseThick" />
            <div>
              Removed
            </div>
          </div>
          <div v-if="isAdding" class="align-center d-flex" :class="labelClass">
            <v-icon class="mr-1" :icon="mdiCheckBold" />
            <div>
              Added
            </div>
          </div>
        </v-btn>
      </template>
      <v-list
        v-if="!groupsLoading"
        density="compact"
        variant="flat"
      >
        <v-list-item v-if="!_filter(currentUser.myCuratedGroups, ['domain', domain]).length" disabled>
          <span class="px-3 py-1 text-no-wrap">You have no {{ domainLabel(false) }}s.</span>
        </v-list-item>
        <v-list-item
          v-for="group in _filter(currentUser.myCuratedGroups, ['domain', domain])"
          :key="group.id"
          density="compact"
          class="py-0"
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
            width="600"
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
import CreateCuratedGroupModal from '@/components/curated/CreateCuratedGroupModal'
import {
  addStudentsToCuratedGroup,
  createCuratedGroup,
  removeFromCuratedGroup
} from '@/api/curated'
import {alertScreenReader} from '@/lib/utils'
import {describeCuratedGroupDomain} from '@/berkeley'
import {filter as _filter, includes, map, without} from 'lodash'
import {mdiCheckBold, mdiCloseThick, mdiMenuDown, mdiPlus} from '@mdi/js'
import {putFocusNextTick} from '@/lib/utils'
import {computed, onMounted, onUnmounted, ref} from 'vue'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  buttonVariant: {
    default: 'text',
    required: false,
    type: String
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

const groupCheckboxClick = group => {
  if (includes(checkedGroups.value, group.id)) {
    isRemoving.value = true
    const done = () => {
      checkedGroups.value = without(checkedGroups.value, group.id)
      isRemoving.value = false
      putFocusNextTick(menuButtonId.value)
      alertScreenReader(`${props.student.name} removed from "${group.name}"`)
    }
    removeFromCuratedGroup(group.id, props.student.sid).finally(() =>
      setTimeout(done, confirmationTimeout.value)
    )
  } else {
    isAdding.value = true
    const done = () => {
      checkedGroups.value.push(group.id)
      isAdding.value = false
      putFocusNextTick(menuButtonId.value)
      alertScreenReader(`${props.student.name} added to "${group.name}"`)
    }
    addStudentsToCuratedGroup(group.id, [props.student.sid]).finally(() => setTimeout(done, confirmationTimeout.value))
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

const onUpdateMyCuratedGroups = domain => {
  if (domain === props.domain) {
    refresh()
  }
}

const refresh = () => {
  const containsSid = group => {
    return includes(group.sids, props.student.sid)
  }
  checkedGroups.value = map(_filter(contextStore.currentUser.myCuratedGroups, containsSid), 'id')
  groupsLoading.value = false
}
</script>

<style scoped>
.opacity-zero {
  opacity: 0;
}
</style>
