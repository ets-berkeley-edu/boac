<template>
  <v-badge
    v-if="currentUser.myUnreadMessageCount"
    id="header-menu-messages-count"
    :aria-label="pluralize('new message', currentUser.myUnreadMessageCount)"
    class="font-size-14 font-weight-bold v-badge-override"
    color="category-alert"
    :content="currentUser.myUnreadMessageCount"
    inline
    max="99"
  />
</template>

<script setup lang="ts">
import {pluralize} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
</script>
