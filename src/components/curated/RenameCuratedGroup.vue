<template>
  <v-card class="py-1 w-100" flat>
    <div class="d-flex flex-wrap flex-sm-nowrap">
      <v-text-field
        id="rename-curated-group-input"
        v-model="name"
        aria-describedby="rename-cohort-input-messages"
        :aria-invalid="!!errorMessage"
        autocomplete="on"
        class="flex-1-1 mr-3 mb-3"
        counter="255"
        density="comfortable"
        :disabled="isSaving"
        :error="!!errorMessage"
        :error-messages="errorMessage"
        :label="`${describeCuratedGroupDomain(domain.value, true)} Name`"
        :maxlength="maxlength"
        persistent-counter
        required
        :rules="[validate]"
        validate-on="lazy invalid-input"
        @keyup.enter="rename"
        @keyup.esc="exitRenameMode"
      >
        <template #counter="{max, value}">
          <CharacterCount :count="toInt(value)" id-prefix="rename-curated-group" :max="toInt(max)" />
        </template>
        <template #message="{message}">
          <v-alert
            id="rename-cohort-error"
            class="font-size-14 line-height-normal"
            density="compact"
            role="none"
            :text="message"
            type="error"
            variant="tonal"
          />
        </template>
      </v-text-field>
      <div class="d-flex ml-auto w-100 w-sm-auto">
        <ProgressButton
          id="rename-curated-group-confirm"
          :action="rename"
          :aria-disabled="isEmpty(name) || isInvalid"
          :aria-label="`Rename ${describeCuratedGroupDomain(domain.value, false)}`"
          class="mr-1"
          :class="{'w-50': xs}"
          :disabled="isSaving"
          height="48px"
          :in-progress="isSaving"
          :text="isSaving ? 'Renaming' : 'Rename'"
        />
        <v-btn
          id="rename-curated-group-cancel"
          :aria-label="`Cancel Rename ${describeCuratedGroupDomain(domain.value, false)}`"
          :class="{'w-50': xs}"
          :disabled="isSaving"
          height="48px"
          text="Cancel"
          variant="text"
          @click="exitRenameMode"
        />
      </div>
    </div>
  </v-card>
</template>

<script setup>
import {isEmpty} from 'lodash'
import {onMounted, ref} from 'vue'
import {storeToRefs} from 'pinia'
import {useDisplay} from 'vuetify'
import CharacterCount from '@/components/util/CharacterCount'
import ProgressButton from '@/components/util/ProgressButton'
import {alertScreenReader, putFocusNextTick, setPageTitle, toInt} from '@/lib/utils'
import {describeCuratedGroupDomain} from '@/lib/berkeley-utils'
import {renameCuratedGroup} from '@/api/curated'
import {useCuratedGroupStore} from '@/stores/curated-group/index'
import {validateCohortName} from '@/lib/cohort'

const curatedStore = useCuratedGroupStore()
const {curatedGroupId, curatedGroupName, domain} = storeToRefs(curatedStore)
const isSaving = ref(false)
const errorMessage = ref('')
const isInvalid = ref(true)
const maxlength = 255
const name = ref(undefined)
const {xs} = useDisplay()

onMounted(() => {
  name.value = curatedGroupName.value
})

const exitRenameMode = () => {
  reset()
  curatedStore.resetMode()
  alertScreenReader('Canceled rename')
  putFocusNextTick('rename-curated-group-button')
}
const reset = () => {
  isSaving.value = false
  name.value = ''
  errorMessage.value = ''
  isInvalid.value = false
}

const rename = () => {
  if (true !== validate()) {
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

const validate = () => {
  const result = validateCohortName({id: curatedGroupId.value, name: name.value})
  if (result === true) {
    errorMessage.value = ''
    isInvalid.value = false
  } else {
    errorMessage.value = result
    isInvalid.value = true
  }
  return result
}
</script>
