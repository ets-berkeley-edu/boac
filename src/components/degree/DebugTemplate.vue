<template>
  <div class="border-top pt-2">
    <div class="py-1">
      <router-link
        v-if="degreeStore.parentTemplateUpdatedAt"
        id="degree-template-source"
        target="_blank"
        :to="`/degree/${degreeStore.parentTemplateId}`"
      >
        Created from template <span class="sr-only"> (will open new browser tab)</span>
        <v-icon :icon="mdiOpenInNew" size="14" />
      </router-link>
    </div>
    <div class="default-margins">
      <div class="pb-1">
        <v-btn
          class="px-0 text-primary"
          :class="degreeStore.disableButtons ? 'text-primary' : 'text-black-50'"
          density="compact"
          :disabled="!degreeStore.disableButtons"
          flat
          :prepend-icon="mdiPlayCircleOutline"
          text="Force buttons to enable"
          variant="text"
          @click="() => degreeStore.setDisableButtons(false)"
        />
      </div>
      <div>
        <v-btn
          class="px-0 text-primary"
          :class="degreeStore.disableButtons ? 'text-primary' : 'text-black-50'"
          density="compact"
          flat
          :prepend-icon="mdiBug"
          :text="showDebug ? 'Hide debug' : 'Show debug'"
          variant="text"
          @click="() => showDebug = !showDebug"
        />
      </div>
      <v-expand-transition>
        <div v-if="showDebug" class="pa-3">
          <pre>{{ degreeStore.degreeEditSessionToString }}</pre>
        </div>
      </v-expand-transition>
    </div>
  </div>
</template>

<script setup>
import {mdiBug, mdiOpenInNew, mdiPlayCircleOutline} from '@mdi/js'
import {ref} from 'vue'
import {useDegreeStore} from '@/stores/degree-edit-session/index'

const degreeStore = useDegreeStore()
const showDebug = ref(false)
</script>
