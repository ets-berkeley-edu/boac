<template>
  <div class="border-top pt-2">
    <div class="py-1">
      <router-link
        v-if="degreeStore.parentTemplateUpdatedAt"
        id="degree-template-source"
        target="_blank"
        :to="`/degree/${degreeStore.parentTemplateId}`"
      >
        <v-icon :icon="mdiOpenInNew" />
        Created from template <span class="sr-only"> (will open new browser tab)</span>
      </router-link>
    </div>
    <div class="pb-1">
      <v-btn
        class="px-0"
        :disabled="!degreeStore.disableButtons"
        variant="text"
        @click="degreeStore.setDisableButtons(false)"
      >
        <v-icon
          :class="degreeStore.disableButtons ? 'text-primary' : 'text-black-50'"
          :icon="mdiPlayCircleOutline"
        />
        Force buttons to enable
      </v-btn>
    </div>
    <div class="align-center d-flex">
      <div class="pr-1">
        <v-icon :icon="mdiBug" />
      </div>
      <div class="pr-2">
        Debug
      </div>
      [<v-btn class="ma-0 pa-0" variant="text" @click="showDebug = !showDebug">{{ showDebug ? 'hide' : 'show' }}</v-btn>]
    </div>
    <v-expand-transition name="drawer">
      <pre v-if="showDebug">{{ degreeStore.degreeEditSessionToString }}</pre>
    </v-expand-transition>
  </div>
</template>

<script setup>
import {mdiBug, mdiOpenInNew, mdiPlayCircleOutline} from '@mdi/js'
import {ref} from 'vue'
import {useDegreeStore} from '@/stores/degree-edit-session/index'

const degreeStore = useDegreeStore()
const showDebug = ref(false)
</script>
