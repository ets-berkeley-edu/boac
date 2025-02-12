<template>
  <v-card class="py-1 w-100" flat>
    <div class="align-start d-flex flex-wrap">
      <v-text-field
        id="rename-curated-group-input"
        v-model="name"
        :aria-invalid="!name"
        :aria-label="`${describeCuratedGroupDomain(domain, true)} name`"
        autocomplete="off"
        class="v-input-details-override mr-3"
        counter="255"
        density="comfortable"
        :disabled="isSaving"
        :label="`${describeCuratedGroupDomain(domain.value, true)} Name`"
        :maxlength="maxlength"
        persistent-counter
        required
        :rules="[() => isValidName]"
        validate-on="lazy input"
        @keyup.enter="rename"
        @keyup.esc="exitRenameMode"
      >
        <template #counter>
          <div>
            {{ size(name) ? `${maxlength} character limit (${maxlength - size(name)} left)` : `${maxlength} character limit` }}
          </div>
        </template>
      </v-text-field>
      <span
        v-if="size(name) === maxlength"
        aria-live="polite"
        class="sr-only"
        role="alert"
      >
        Name cannot exceed {{ maxlength }} characters.
      </span>
      <div>
        <ProgressButton
          id="rename-curated-group-confirm"
          :action="rename"
          :aria-label="`Rename ${describeCuratedGroupDomain(domain.value, false)}`"
          class="mr-1"
          :disabled="isValidName !== true || isSaving"
          :in-progress="isSaving"
          size="large"
          :text="isSaving ? 'Renaming' : 'Rename'"
        />
        <v-btn
          id="rename-curated-group-cancel"
          :aria-label="`Cancel Rename ${describeCuratedGroupDomain(domain.value, false)}`"
          :disabled="isSaving"
          size="large"
          text="Cancel"
          variant="text"
          @click="exitRenameMode"
        />
      </div>
    </div>
  </v-card>
</template>

<script setup>
import {computed, onMounted, ref} from 'vue'
import {size} from 'lodash'
import {storeToRefs} from 'pinia'
import ProgressButton from '@/components/util/ProgressButton'
import {alertScreenReader, putFocusNextTick, setPageTitle} from '@/lib/utils'
import {describeCuratedGroupDomain} from '@/lib/berkeley-utils'
import {renameCuratedGroup} from '@/api/curated'
import {useCuratedGroupStore} from '@/stores/curated-group/index'
import {validateCohortName} from '@/lib/cohort'

const curatedStore = useCuratedGroupStore()
const {curatedGroupId, curatedGroupName, domain} = storeToRefs(curatedStore)
const isSaving = ref(false)
const isValidName = computed(() => validateCohortName({id: curatedGroupId.value, name: name.value}))
const maxlength = 255
const name = ref(undefined)

onMounted(() => {
  name.value = curatedGroupName.value
})

const exitRenameMode = () => {
  curatedStore.resetMode()
  alertScreenReader('Canceled rename')
  putFocusNextTick('rename-curated-group-button')
}

const rename = () => {
  if (validateCohortName({name: name.value}) !== true) {
    putFocusNextTick('rename-curated-group-input')
  } else {
    alertScreenReader(`Renaming ${describeCuratedGroupDomain(domain.value)}`)
    isSaving.value = true
    renameCuratedGroup(curatedGroupId.value, domain.value, name.value).then(curatedGroup => {
      curatedStore.setCuratedGroupName(curatedGroup.name)
      setPageTitle(curatedGroupName.value)
      exitRenameMode()
      isSaving.value = false
      alertScreenReader(`${describeCuratedGroupDomain(domain.value, true)} renamed to ${curatedGroup.name}`)
      putFocusNextTick('rename-curated-group-button"')
    })
  }
}
</script>
