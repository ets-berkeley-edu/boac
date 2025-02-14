<template>
  <div class="name-container">
    <div class="icons">
      <span v-if="!user.canAccessCanvasData">
        <span class="c-letter">C</span>
        <span class="slash text-error">\</span>
      </span>
      <span v-if="!user.canAccessAdvisingData" class="advising-data">
        <span class="slash-2 text-error">\</span>
        <v-icon :icon="mdiNoteOutline" size="small" />
      </span>
    </div>
    <div v-if="!user.name" class="name">
      <span class="text-medium-emphasis">(Name unavailable)</span>
    </div>
    <div v-if="user.name" class="name">
      <a
        :id="`directory-link-${user.uid}`"
        :aria-label="`${user.name} UC Berkeley Directory page (opens in new window)`"
        :href="`https://www.berkeley.edu/directory/results?search-term=${user.name}`"
        target="_blank"
      >
        {{ user.name }}
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {mdiNoteOutline} from '@mdi/js'
import type {BoaUser} from '@/lib/types'

defineProps({
  user: {
    required: true,
    type: Object as PropType<BoaUser>
  }
})
</script>

<style scoped>
.advising-data {
  position: relative;
  left: -8px;
}
.c-letter {
  position: relative;
  top: 1px;
  left: 1px;
}
.icons {
  position: relative;
  top: -1px;
  display: inline-block;
}
.name {
  position: relative;
  display: inline-block;
}
.name-container {
  position: relative;
  top: -1px;
}
.slash {
  font-size: 22px;
  left: -8px;
  position: relative;
  top: 4px;
}
.slash-2 {
  font-size: 22px;
  left: 12px;
  top: 4px;
  position: relative;
  z-index: 100;
}
</style>
