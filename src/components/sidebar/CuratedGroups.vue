<template>
  <div>
    <div class="d-flex justify-content-between mb-1 sidebar-row-link">
      <div class="ml-1" :class="headerClass">
        {{ domain === 'admitted_students' ? 'CE3 Groups' : 'Curated Groups' }}
      </div>
      <div class="ml-1 mr-2">
        <NavLink
          :id="`create-${idFragment}-from-sidebar`"
          :aria-label="`Create a new ${domainLabel(false)}.`"
          class="sidebar-create-link"
          path="/curate"
          :query-args="{'domain': domain}"
        >
          <font-awesome icon="plus" :class="headerClass" />
        </NavLink>
      </div>
    </div>
    <div
      v-for="(group, index) in _filter(currentUser.myCuratedGroups, ['domain', domain])"
      :key="group.id"
      class="d-flex justify-content-between sidebar-row-link"
    >
      <div class="ml-1 truncate-with-ellipsis">
        <NavLink
          :id="`sidebar-${idFragment}-${index}`"
          :aria-label="`${_capitalize(domainLabel(false))} ${group.name} has ${group.totalStudentCount} students.`"
          :path="`/curated/${group.id}`"
        >
          {{ group.name }}
        </NavLink>
      </div>
      <div class="ml-1 mr-2">
        <span
          :id="`sidebar-${idFragment}-${index}-count`"
          class="sidebar-pill"
        >{{ group.totalStudentCount }}<span class="sr-only"> {{ pluralize('student', group.totalStudentCount) }}</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import NavLink from '@/components/util/NavLink'
import Util from '@/mixins/Util'
import {describeCuratedGroupDomain} from '@/berkeley'

export default {
  name: 'CuratedGroups',
  components: {NavLink},
  mixins: [Context, Util],
  props: {
    domain: {
      type: String,
      required: true
    },
    headerClass: {
      default: 'sidebar-header',
      required: false,
      type: String
    }
  },
  data: () => ({
    idFragment: undefined
  }),
  created() {
    this.idFragment = this.domainLabel(false).replace(' ', '-')
  },
  methods: {
    domainLabel(capitalize) {
      return describeCuratedGroupDomain(this.domain, capitalize)
    }
  }
}
</script>
