<template>
  <div class="align-items-center d-flex justify-content-between link-container mb-1 pl-3 pr-4">
    <div class="truncate-with-ellipsis">
      <NavLink
        id="link-to-draft-notes"
        path="/note/drafts"
      >
        Draft Notes
      </NavLink>
    </div>
    <div>
      <span
        id="draft-note-count"
        class="sidebar-pill"
      >{{ $currentUser.myDraftNoteCount }}<span class="sr-only"> {{ pluralize('draft', $currentUser.myDraftNoteCount) }}</span>
      </span>
    </div>
  </div>
</template>

<script>
import NavLink from '@/components/util/NavLink.vue'
import Util from '@/mixins/Util.vue'

export default {
  name: 'LinkToDraftNotes',
  components: {NavLink},
  mixins: [Util]
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
