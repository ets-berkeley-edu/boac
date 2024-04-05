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
        <v-icon color="white" :icon="mdiPlus" size="24" />
      </NavLink>
    </div>
    <div
      v-for="(group, index) in filter(get(useContextStore().currentUser, 'myCuratedGroups'), ['domain', domain])"
      :key="group.id"
      class="d-flex justify-space-between align-center pl-2 sidebar-row-link"
    >
      <NavLink
        :id="`sidebar-${idFragment}-${index}`"
        :aria-label="`${capitalize(domainLabel(false))} ${group.name} has ${group.totalStudentCount} students.`"
        class="truncate-with-ellipsis"
        :path="`/curated/${group.id}`"
      >
        {{ group.name }}
      </NavLink>
      <div class="pl-1 pr-3">
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
import NavLink from '@/components/util/NavLink'
import {describeCuratedGroupDomain} from '@/berkeley'
import {capitalize, filter, get} from 'lodash'
import {pluralize} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

export default {
  name: 'CuratedGroups',
  components: {NavLink},
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
    },
    get,
    pluralize,
    useContextStore
  }
}
</script>
