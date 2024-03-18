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
      >{{ currentUser.myDraftNoteCount }}<span class="sr-only"> {{ pluralize('draft', currentUser.myDraftNoteCount) }}</span>
      </span>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import NavLink from '@/components/util/NavLink.vue'
import Util from '@/mixins/Util.vue'

export default {
  name: 'LinkToDraftNotes',
  components: {NavLink},
  mixins: [Context, Util]
}
</script>
