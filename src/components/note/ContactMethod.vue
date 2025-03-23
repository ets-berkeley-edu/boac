<template>
  <div>
    <label
      id="contact-type-label"
      class="font-size-16 font-weight-bold"
      for="contact-type-options"
    >
      Contact Method
    </label>
    <div class="mt-1">
      <v-radio-group
        id="contact-type-options"
        aria-describedby="contact-type-label"
        color="primary"
        density="compact"
        :disabled="noteStore.isSaving || noteStore.boaSessionExpired"
        hide-details
        :model-value="noteStore.model.contactType"
        :ripple="false"
        @update:model-value="onChangeContactType"
      >
        <v-radio
          id="contact-option-none-radio-button"
          label="None"
          :ripple="false"
          :value="null"
        />
        <template v-for="(contactType, index) in contactTypes" :key="contactType.value">
          <v-radio
            v-if="isCurrentUserPeerAdvisor ? contactType.isAvailableToPeerAdvisors : true"
            :id="`contact-option-${index}-radio-button`"
            :label="contactType.value"
            :ripple="false"
            :value="contactType.value"
          />
        </template>
      </v-radio-group>
    </div>
  </div>
</template>

<script setup lang="ts">
import {isPeerAdvisor} from '@/lib/boa-user'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

const contextStore = useContextStore()
const contactTypes = contextStore.config.noteContactTypes
const isCurrentUserPeerAdvisor = isPeerAdvisor(contextStore.currentUser)
const noteStore = useNoteStore()

const onChangeContactType = (value: string) => noteStore.setContactType(value)
</script>
