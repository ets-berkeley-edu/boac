<template>
  <div class="align-center d-flex justify-space-between pretty-hover pr-2 pl-3">
    <NavLink
      id="link-to-draft-notes"
      class="font-size-18 font-weight-bold text-secondary truncate-with-ellipsis"
      path="/note/drafts"
    >
      Draft notes<span class="sr-only">: {{ pluralize('draft', currentUser.myDraftNoteCount) }}
      </span>
    </NavLink>
    <PillCount
      id="sidebar-draft-notes-count"
      :aria-hidden="true"
      class="text-quaternary sidebar-pill"
      color="secondary"
    >
      {{ currentUser.myDraftNoteCount }}
    </PillCount>
  </div>
</template>

<script setup>
import NavLink from '@/components/util/NavLink'
import PillCount from '@/components/util/PillCount'
import {pluralize} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const currentUser = useContextStore().currentUser
</script>
