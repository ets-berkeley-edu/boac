<template>
  <div class="align-center d-flex justify-space-between pretty-hover">
    <NavLink
      id="link-to-draft-notes"
      class="font-size-18 font-weight-bold text-secondary truncate-with-ellipsis"
      path="/note/drafts"
    >
      Draft notes<span class="sr-only">: {{ pluralize('draft', get(currentUser, 'myDraftNoteCount')) }}
      </span>
    </NavLink>
    <PillCount
      id="sidebar-draft-notes-count"
      :aria-hidden="true"
      class="text-quaternary sidebar-pill"
      color="secondary"
    >
      {{ get(currentUser, 'myDraftNoteCount') }}
    </PillCount>
  </div>
</template>

<script setup>
import NavLink from '@/components/util/NavLink'
import PillCount from '@/components/util/PillCount'
import {get} from 'lodash'
import {pluralize} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const currentUser = useContextStore().currentUser
</script>
