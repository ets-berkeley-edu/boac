<template>
  <v-container fluid>
    <v-row align-v="center" class="pt-2" no-gutters>
      <v-col cols="2">
        <div class="pr-3">
          <select
            id="user-filter-options"
            v-model="filter.type"
            class="select-menu w-100"
            :disabled="disabled"
          >
            <option
              v-for="option in [
                {name: 'Search', value: 'search'},
                {name: 'BOA Admins', value: 'admins'},
                {name: 'Filter', value: 'filter'}
              ]"
              :key="option.value"
              :value="option.value"
            >
              {{ option.name }}
            </option>
          </select>
        </div>
      </v-col>
      <v-col cols="10">
        <div v-if="filter.type === 'search'">
          <span id="user-search-input" class="sr-only">Search for user. Expect auto-suggest as you type name or UID.</span>
          <v-autocomplete
            id="search-user-input"
            autocomplete="off"
            base-color="body"
            :class="{'demo-mode-blur': currentUser.inDemoMode}"
            color="body"
            density="compact"
            :disabled="disabled"
            hide-details
            :hide-no-data="!!(size(autocompleteInput) < 3 || disabled || isSuggesting || suggestedUsers.length)"
            item-title="text"
            :items="suggestedUsers"
            label="Enter name or UID"
            :maxlength="72"
            :menu-icon="undefined"
            :menu-props="{'content-class': currentUser.inDemoMode ? 'demo-mode-blur' : ''}"
            :model-value="userSelection"
            no-data-text="No match found"
            return-object
            variant="outlined"
            @update:model-value="onUpdateAutocompleteModel"
            @update:search="onUpdateSearch"
          >
            <template #append-inner>
              <v-progress-circular
                v-if="isSuggesting"
                color="primary"
                indeterminate
                :size="18"
                :width="3"
              />
            </template>
          </v-autocomplete>
        </div>
        <div v-if="filter.type === 'filter'" class="d-flex flex-wrap">
          <div class="pr-2">
            <select
              id="department-select-list"
              v-model="filter.deptCode"
              aria-label="department"
              class="select-menu mb-1"
              :disabled="disabled"
              @update:model-value="fetchUsers('user-permission-options')"
            >
              <option
                v-for="option in [{id: -1, deptCode: undefined, deptName: 'All'}, ...allBerkeleyDepartments]"
                :id="normalizeId(`department-option-${option.deptCode}`)"
                :key="option.deptCode"
                :value="option.deptCode"
              >
                {{ option.deptName }}
              </option>
            </select>
          </div>
          <div class="pr-2">
            <select
              id="user-permission-options"
              v-model="filter.role"
              aria-label="user permissions"
              class="select-menu mb-1"
              :disabled="disabled"
              @update:model-value="fetchUsers('user-status-options')"
            >
              <option
                v-for="option in [
                  {name: 'All', value: undefined},
                  {name: 'Advisors', value: 'advisor'},
                  {name: 'No Canvas Data', value: 'noCanvasDataAccess'},
                  {name: 'No Notes or Appointments', value: 'noAdvisingDataAccess'},
                  {name: 'Directors', value: 'director'}
                ]"
                :id="`user-permission-${toLower(option.value || option.name)}`"
                :key="option.value"
                :value="option.value"
              >
                {{ option.name }}
              </option>
            </select>
          </div>
          <div>
            <select
              id="user-status-options"
              v-model="filter.status"
              aria-label="user status"
              class="select-menu"
              :disabled="disabled"
              @update:model-value="fetchUsers('user-status-options')"
            >
              <option
                v-for="option in [
                  {name: 'All', value: undefined},
                  {name: 'Active', value: 'active'},
                  {name: 'Deleted', value: 'deleted'},
                  {name: 'Blocked', value: 'blocked'}
                ]"
                :id="`user-permission-${toLower(option.value || option.name)}`"
                :key="option.value"
                :value="option.value"
              >
                {{ option.name }}
              </option>
            </select>
          </div>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {debounce, isUndefined, map, size, toLower, trim} from 'lodash'
import {ref} from 'vue'
import type {BoaUsersFilter, Department, SelectOption} from '@/lib/types'
import {escapeForRegExp, normalizeId} from '@/lib/utils'
import {userAutocomplete} from '@/api/user'
import {useContextStore} from '@/stores/context'

const filter = defineModel<BoaUsersFilter>({
  required: true,
  type: Object as PropType<BoaUsersFilter>
})

const props = defineProps({
  allBerkeleyDepartments: {
    required: true,
    type: Array as PropType<Array<Department>>
  },
  disabled: {
    required: false,
    type: Boolean
  },
  fetchUsers: {
    required: true,
    type: Function
  }
})

const autocompleteInput = ref<string | undefined>(undefined)
const currentUser = useContextStore().currentUser
const isSuggesting = ref(false)
const suggestedUsers = ref<SelectOption<object>[]>([])
const userSelection = ref()

const onUpdateAutocompleteModel = user => {
  userSelection.value = user
  props.fetchUsers()
}

const onUpdateSearch = debounce(query => {
  autocompleteInput.value = query && trim(escapeForRegExp(query).replace(/[^\w ]+/g, ''))
  if (!isUndefined(autocompleteInput.value) && autocompleteInput.value.length) {
    isSuggesting.value = true
    userAutocomplete(autocompleteInput.value, new AbortController()).then(results => {
      suggestedUsers.value = map(results, result => ({text: result.label, value: result}))
      isSuggesting.value = false
    })
  }
}, 500)
</script>

<style scoped>
.select-menu {
  height: 40px;
}
</style>
