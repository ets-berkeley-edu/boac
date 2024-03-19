<template>
  <div class="align-center d-flex justify-space-between mb-1 pl-1 pr-2 sidebar-row-link">
    <NavLink
      id="link-to-draft-notes"
      class="truncate-with-ellipsis"
      path="/note/drafts"
    >
      Draft Notes
    </NavLink>
    <div>
      <span
        id="draft-note-count"
        class="sidebar-pill"
      >{{ draftNoteCount }}<span class="sr-only"> {{ draftNoteLabel }}</span>
      </span>
    </div>
  </div>
</template>

<script>
import NavLink from '@/components/util/NavLink.vue'
import {get} from 'lodash'
import {pluralize} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

export default {
  name: 'LinkToDraftNotes',
  components: {NavLink},
  computed: {
    draftNoteCount() {
      return get(useContextStore().currentUser, 'myDraftNoteCount')
    },
    draftNoteLabel() {
      return pluralize('draft', get(useContextStore().currentUser, 'myDraftNoteCount'))
    }
  }
}
</script>
