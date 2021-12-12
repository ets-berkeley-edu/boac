<template>
  <div>
    <div class="d-flex justify-content-between mb-1 sidebar-row-link">
      <div class="ml-1" :class="headerClass">
        {{ headerText }}
      </div>
      <div class="ml-1 mr-2">
        <NavLink
          id="create-curated-group-from-sidebar"
          aria-label="Create a new curated group"
          class="sidebar-create-link"
          path="/curate"
          :query-args="{'domain': domain}"
        >
          <font-awesome icon="plus" :class="headerClass" />
        </NavLink>
      </div>
    </div>
    <div
      v-for="(group, index) in $_.filter($currentUser.myCuratedGroups, ['domain', domain])"
      :key="group.id"
      class="d-flex justify-content-between sidebar-row-link"
    >
      <div class="ml-1 truncate-with-ellipsis">
        <NavLink
          :id="`sidebar-curated-group-${index}`"
          :aria-label="'Curated group ' + group.name + ' has ' + group.totalStudentCount + ' students'"
          :path="`/curated/${group.id}`"
        >
          {{ group.name }}
        </NavLink>
      </div>
      <div class="ml-1 mr-2">
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
import NavLink from '@/components/util/NavLink'
import Util from '@/mixins/Util'

export default {
  name: 'CuratedGroups',
  components: {NavLink},
  mixins: [Util],
  props: {
    domain: {
      type: String,
      required: true
    },
    headerClass: {
      default: 'sidebar-header',
      required: false,
      type: String
    },
    headerText: {
      default: 'Curated Groups',
      required: false,
      type: String
    }
  }
}
</script>
