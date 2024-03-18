<template>
  <div>
    <div class="d-flex justify-space-between align-center mb-1 pl-1 pr-2 sidebar-row-link">
      <div :class="headerClass">
        {{ domain === 'admitted_students' ? 'CE3 Groups' : 'Curated Groups' }}
      </div>
      <NavLink
        :id="`create-${idFragment}-from-sidebar`"
        :aria-label="`Create a new ${domainLabel(false)}.`"
        class="sidebar-create-link"
        path="/curate"
        :query-args="{'domain': domain}"
      >
        <v-icon color="white" :icon="mdiPlus" size="large" />
      </NavLink>
    </div>
    <div
      v-for="(group, index) in _filter(currentUser.myCuratedGroups, ['domain', domain])"
      :key="group.id"
      class="d-flex justify-space-between align-center pl-1 sidebar-row-link"
    >
      <NavLink
        :id="`sidebar-${idFragment}-${index}`"
        :aria-label="`${_capitalize(domainLabel(false))} ${group.name} has ${group.totalStudentCount} students.`"
        class="truncate-with-ellipsis"
        :path="`/curated/${group.id}`"
      >
        {{ group.name }}
      </NavLink>
      <div class="pl-1 pr-2">
        <span
          :id="`sidebar-${idFragment}-${index}-count`"
          class="sidebar-pill"
        >{{ group.totalStudentCount }}<span class="sr-only"> {{ pluralize('student', group.totalStudentCount) }}</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import {mdiPlus} from '@mdi/js'
</script>

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
