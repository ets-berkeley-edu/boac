<template>
  <div class="align-center d-flex justify-space-between link-container">
    <NavLink
      id="link-to-draft-notes"
      class="font-size-18 font-weight-bold truncate-with-ellipsis"
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

<style scoped>
.link-container {
  color: #8bbdda;
  font-size: 16px;
}
.link-container:hover,
.link-container:focus,
.link-container:active {
  border: 0;
  color: #f0ad4e;
  text-decoration: none;
  -moz-outline-style: none;
}
.link-container:hover .sidebar-pill,
.link-container:focus .sidebar-pill,
.link-container:active .sidebar-pill {
  color: #083456;
}
.link-container a:link,
.link-container a:visited {
  text-decoration: none;
  border: 0;
  color: inherit;
  -moz-outline-style: none;
}
</style>
