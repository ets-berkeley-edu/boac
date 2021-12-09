<template>
  <div>
    <div class="d-flex justify-content-between mb-1 sidebar-row-link">
      <div class="ml-2 sidebar-header">
        {{ headerText }}
      </div>
      <div class="ml-2 mr-2">
        <NavLink
          id="create-curated-group-from-sidebar"
          aria-label="Create a new curated group"
          class="sidebar-create-link"
          path="/curate"
          :query-args="{'domain': domain}"
        >
          <font-awesome icon="plus" class="sidebar-header" />
        </NavLink>
      </div>
    </div>
    <div
      v-for="(group, index) in groups"
      :key="group.id"
      class="d-flex justify-content-between sidebar-row-link"
    >
      <div class="ml-2 truncate-with-ellipsis">
        <NavLink
          :id="`sidebar-curated-group-${index}`"
          :aria-label="'Curated group ' + group.name + ' has ' + group.totalStudentCount + ' students'"
          :path="`/curated/${group.id}`"
        >
          {{ group.name }}
        </NavLink>
      </div>
      <div class="ml-2 mr-2">
        <span
          :id="`sidebar-curated-group-${index}-count`"
          class="sidebar-pill"
        >{{ group.totalStudentCount }}<span class="sr-only">{{ pluralize('student', group.totalStudentCount) }}</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import CurrentUserExtras from '@/mixins/CurrentUserExtras'
import NavLink from '@/components/util/NavLink'
import Util from '@/mixins/Util'

export default {
  name: 'CuratedGroups',
  components: {NavLink},
  mixins: [CurrentUserExtras, Util],
  props: {
    domain: {
      type: String,
      required: true
    },
    groups: {
      type: Array,
      required: true
    },
    headerText: {
      default: 'Curated Groups',
      required: false,
      type: String
    }
  }
}
</script>
