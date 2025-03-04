<template>
  <div>
    <div
      v-if="text.length <= lengthTruncateButtonText"
      class="align-start"
      :class="{'demo-mode-blur': currentUser.inDemoMode}"
      v-html="trim(text)"
    />
    <div
      v-if="text.length > lengthTruncateButtonText"
      class="align-start"
      :class="{'demo-mode-blur': currentUser.inDemoMode}"
      v-html="truncate(trim(text), {length: lengthTruncateButtonText})"
    />
  </div>
</template>

<script setup lang="ts">
import {trim, truncate} from 'lodash'
import {computed} from 'vue'
import {useDisplay} from 'vuetify'
import {useContextStore} from '@/stores/context'

defineProps({
  text: {
    required: true,
    type: String
  }
})

const currentUser = useContextStore().currentUser
const display = useDisplay()
const lengthTruncateButtonText = computed(() => display.lgAndUp.value ? 60 : (display.mdAndUp.value ? 30 : 16))
</script>
