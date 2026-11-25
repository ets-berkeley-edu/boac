<template>
  <v-menu
    v-model="isMenuOpen"
    :close-on-content-click="false"
    eager
  >
    <template #activator="{ props }">
      <v-btn
        class="opacity-100"
        color="primary"
        density="compact"
        slim
        variant="plain"
        v-bind="props"
      >
        <template #prepend>
          <div
            class="border-md rounded-circle filter-icon"
            :class="{
              'bg-success border-success': !isMenuOpen,
              'text-disabled': isMenuOpen}"
          >
            <v-icon :icon="mdiFilterVariant" size="0.875rem" />
          </div>
        </template>
        Filter
      </v-btn>
    </template>
    <v-list
      color="primary"
      density="compact"
      item-props
      :items="filterOptions"
      menu
      select-strategy="leaf"
      selectable
      :selected="filtersApplied"
      @click:select="onSelectOption"
    >
      <template #prepend="{ isSelected }">
        <v-list-item-action start>
          <div class="checkmark-container">
            <v-icon v-if="isSelected" :icon="mdiCheckBold" />
          </div>
        </v-list-item-action>
      </template>
    </v-list>
  </v-menu>
</template>

<script setup lang="ts">
import {ref} from 'vue'
import {concat, isEmpty, without} from 'lodash'
import {mdiCheckBold, mdiFilterVariant} from '@mdi/js'

const divider = {class: 'my-2', color: 'primary', opacity: '0.4', thickness: '2px', type: 'divider'}
const filterOptions = [
  {density: 'compact', title: 'Show All', value: 'all'},
  divider,
  {density: 'compact', title: 'Read', value: 'read'},
  {density: 'compact', title: 'Unread', value: 'unread'},
  divider,
  {density: 'compact', title: 'Notes', value: 'note'},
  {density: 'compact', title: 'Appointments', value: 'appointment'},
  {density: 'compact', title: 'EForms', value: 'eForm'},
]
const filtersApplied = defineModel<string[]>({default: () => ['all']})
const isMenuOpen = ref(false)

const onSelectOption = option => {
  let selected = filtersApplied.value
  if (option.value === true) {
    switch (option.id) {
    case 'all':
      selected = ['all']
      break
    case 'read':
      selected = concat(without(selected, 'all', 'unread'), 'read')
      break
    case 'unread':
      selected = concat(without(selected, 'all', 'read'), 'unread')
      break
    case 'note':
    case 'appointment':
    case 'eForm':
      selected = concat(without(selected, 'all'), option.id)
      break
    default:
      throw new TypeError(`Unrecognized message filter: ${option.id}`)
    }
  } else {
    selected = without(selected, option.id)
  }
  if (isEmpty(selected)) {
    selected = ['all']
  }
  filtersApplied.value = selected
}
</script>

<style scoped>
.checkmark-container {
  width: 24px;
}
.filter-icon {
  box-sizing: content-box;
  height: 1rem;
  max-width: 1rem;
  min-width: 1rem;
  width: 1rem;
}
.filter-icon .v-icon {
  margin-left: -0.1rem;
  margin-top: -0.1rem;
}
</style>
