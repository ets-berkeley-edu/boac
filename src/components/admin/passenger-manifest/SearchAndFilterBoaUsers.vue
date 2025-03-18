<template>
  <div :class="{'component-container': mdAndUp}" class="align-start d-flex">
    <div class="pr-2">
      <select
        id="toggle-user-search-type"
        v-model="filter.type"
        aria-label="Choose how you want to find users: search field or via filters."
        class="select-menu"
        :disabled="disabled"
      >
        <option
          v-for="option in [
            {name: 'Search', value: 'search'},
            {name: 'Filter', value: 'filter'}
          ]"
          :id="`search-type-option-${toLower(option.value || option.name)}`"
          :key="option.value"
          :value="option.value"
        >
          {{ option.name }}
        </option>
      </select>
    </div>
    <div v-if="filter.type === 'search'" class="align-center d-flex w-100">
      <div class="w-50">
        <span id="user-search-input" class="sr-only">Search for user. Expect auto-suggest as you type name or UID.</span>
        <v-autocomplete
          id="search-user-input"
          autocomplete="off"
          base-color="body"
          :class="{'demo-mode-blur': currentUser.inDemoMode}"
          color="body"
          :debounce="500"
          density="compact"
          :disabled="disabled"
          hide-details
          :hide-no-data="true"
          item-title="name"
          :items="suggestedUsers"
          label="Name or UID"
          :loading="isSuggesting"
          :maxlength="72"
          :menu-icon="() => null"
          :menu-props="{'contentClass': currentUser.inDemoMode ? 'demo-mode-blur' : ''}"
          :model-value="userSelection"
          :no-data-text="isSuggesting ? undefined : 'No match found'"
          return-object
          variant="outlined"
          @update:model-value="item => onUpdateAutocompleteModel(item.uid)"
          @update:search="onUpdateSearch"
        />
      </div>
    </div>
    <div v-if="filter.type === 'filter'" :class="{'align-center d-flex': mdAndUp}">
      <div class="pr-2">
        <select
          id="select-user-role"
          v-model="filter.role"
          aria-label="User roles"
          class="select-menu"
          :disabled="disabled"
        >
          <option
            v-for="option in [
              {name: 'All', value: undefined},
              {name: 'Admins', value: 'admin'},
              {name: 'Advisors', value: 'advisor'},
              {name: 'Directors', value: 'director'},
              {name: 'Peer Advisors', value: 'peer_advisor', disabled: !allPeerAdvisingDepartments.length},
              {name: 'Peer Advisor Managers', value: 'peer_advisor_manager', disabled: !allPeerAdvisingDepartments.length}
            ]"
            :id="`role-option-${toLower(option.value || option.name)}`"
            :key="option.value"
            :value="option.value"
          >
            {{ option.name }}
          </option>
        </select>
      </div>
      <div v-if="['advisor', 'director', undefined].includes(filter.role)" :class="{'mt-2': smAndDown}" class="pr-2">
        <select
          id="select-user-department"
          v-model="filter.deptCode"
          aria-label="department"
          class="select-menu"
          :disabled="disabled"
        >
          <option
            v-for="option in [{id: undefined, deptCode: undefined, deptName: 'All'}, ...manifestStore.allBerkeleyDepartments]"
            :id="normalizeId(`department-option-${option.deptCode}`)"
            :key="option.deptCode"
            :value="option.deptCode"
          >
            {{ option.deptName }}
          </option>
        </select>
      </div>
      <div v-if="PEER_ADVISING_ROLE_TYPES.includes(filter.role)" :class="{'mt-2': smAndDown}" class="pr-2">
        <select
          id="select-user-peer-advising-department"
          v-model="filter.peerAdvisingDepartmentId"
          aria-label="department"
          class="select-menu"
          :disabled="disabled"
        >
          <option
            v-for="option in [{id: undefined, name: 'All'}, ...manifestStore.allPeerAdvisingDepartments]"
            :id="normalizeId(`peer-advising-department-option-${option.name}`)"
            :key="option.id"
            :value="option.id"
          >
            {{ option.name }}
          </option>
        </select>
      </div>
      <div :class="{'mt-2': smAndDown}" class="align-center d-flex">
        <div class="mr-3">
          <select
            id="select-user-status"
            v-model="filter.status"
            aria-label="user status"
            class="select-menu"
            :disabled="disabled"
          >
            <option
              v-for="option in [
                {name: 'All', value: undefined},
                {name: 'Active', value: 'active'},
                {name: 'Deleted', value: 'deleted'},
                {name: 'Blocked', value: 'blocked'}
              ]"
              :id="`option-status-${toLower(option.value || option.name)}`"
              :key="option.value"
              :value="option.value"
            >
              {{ option.name }}
            </option>
          </select>
        </div>
        <div v-if="!isFetching">
          <v-btn
            id="submit-user-search-filters"
            aria-label="Submit user search filters"
            color="primary"
            density="comfortable"
            :disabled="disabled"
            :icon="mdiTransferRight"
            @click="() => fetchUsers()"
          />
        </div>
        <div v-if="isFetching">
          <v-progress-circular
            :model-value="counter"
            :indeterminate="true"
            :size="36"
            :width="7"
            :color="['primary', 'warning', 'success'][Math.round(counter / 10) % 3]"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {debounce, size, toLower, trim} from 'lodash'
import {mdiTransferRight} from '@mdi/js'
import {onMounted, onUnmounted, ref, watch} from 'vue'
import {storeToRefs} from 'pinia'
import {useDisplay} from 'vuetify'
import type {SelectOption} from '@/lib/types'
import {PEER_ADVISING_ROLE_TYPES} from '@/lib/berkeley-department'
import {escapeForRegExp, normalizeId, putFocusNextTick} from '@/lib/utils'
import {getUserByUid, userAutocomplete} from '@/api/user'
import {useContextStore} from '@/stores/context'
import {useManifestStore} from '@/stores/manifest'

defineProps({
  fetchUsers: {
    required: true,
    type: Function
  }
})

const manifestStore = useManifestStore()

const autocompleteInput = ref<string | undefined>(undefined)
const counter = ref(0)
const currentUser = useContextStore().currentUser
const intervalId = ref<ReturnType<typeof setTimeout>>()
const isSuggesting = ref(false)
const suggestedUsers = ref<SelectOption<object>[]>([])
const userSelection = ref<SelectOption<object>>()
const {disabled, filter, isFetching, allPeerAdvisingDepartments} = storeToRefs(manifestStore)
const {mdAndUp, smAndDown} = useDisplay()

onMounted(() => {
  return intervalId.value = setInterval(() => {
    counter.value = counter.value === 100 ? 0 : counter.value + 1
  }, 100)
})

onUnmounted(() => clearInterval(intervalId.value))

watch(() => filter.value.type, value => putFocusNextTick(value === 'search' ? 'search-user-input' : 'select-user-role'))
watch(() => filter.value.role, () => putFocusNextTick('select-user-department'))
watch(() => filter.value.deptCode, () => putFocusNextTick('select-user-status'))
watch(() => filter.value.peerAdvisingDepartmentId, () => putFocusNextTick('select-user-status'))
watch(() => filter.value.status, () => putFocusNextTick('submit-user-search-filters'))

const onUpdateAutocompleteModel = (uid: string) => {
  manifestStore.setIsFetching(true)
  getUserByUid(uid, true).then(user => {
    manifestStore.setUsers([user])
    autocompleteInput.value = userSelection.value = undefined
    manifestStore.setIsFetching(false)
  })
}

const onUpdateSearch = debounce((query: string) => {
  const input = query && trim(escapeForRegExp(query).replace(/[^\w ]+/g, ''))
  if (size(input) && input !== autocompleteInput.value) {
    autocompleteInput.value = input
    isSuggesting.value = true
    userAutocomplete(autocompleteInput.value, new AbortController()).then(data => {
      suggestedUsers.value = data
      isSuggesting.value = false
    })
  }
}, 500)
</script>

<style scoped>
.component-container {
  height: 50px !important;
}
.select-menu {
  height: 40px;
}
</style>
