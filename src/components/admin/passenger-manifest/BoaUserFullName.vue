<template>
  <div class="align-center d-flex">
    <div class="align-center d-flex font-size-14" :class="{'mr-2': !user.canAccessCanvasData || !user.canAccessAdvisingData}">
      <div class="mr-3">
        <v-btn
          :id="`edit-${user.uid}`"
          :aria-label="`Edit profile of ${user.name}`"
          color="primary"
          :icon="mdiNoteEditOutline"
          variant="text"
          width="20"
          @click="() => onClickEditUser(index, user.uid)"
        />
      </div>
      <div v-if="!user.canAccessCanvasData" class="font-size-18 mr-1 strikethrough">
        C<span class="sr-only">annot access Canvas data</span>
      </div>
      <div v-if="!user.canAccessAdvisingData" class="strikethrough" style="padding-bottom: 2px;">
        <v-icon :icon="mdiNoteOutline" size="18" />
      </div>
    </div>
    <div v-if="!user.name" class="name text-medium-emphasis">
      (Name unavailable)
    </div>
    <div v-if="user.name">
      <a
        :id="`directory-link-${user.uid}`"
        :aria-label="`${user.name} UC Berkeley Directory page (opens in new window)`"
        style="word-wrap: break-word;"
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
import {mdiNoteEditOutline, mdiNoteOutline} from '@mdi/js'
import type {BoaUser} from '@/lib/types'

defineProps({
  index: {
    required: true,
    type: Number
  },
  onClickEditUser: {
    required: true,
    type: Function
  },
  user: {
    required: true,
    type: Object as PropType<BoaUser>
  }
})
</script>

<style scoped>
.strikethrough {
  position: relative;
}
.strikethrough:before {
  position: absolute;
  color: #cf1715;
  content: "";
  left: 0;
  top: 50%;
  right: 0;
  border-top: 3px solid;
  border-color: inherit;
  -ms-transform:rotate(-45deg);
  transform:rotate(-45deg);
}
</style>
