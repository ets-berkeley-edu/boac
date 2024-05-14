<template>
  <div v-if="!loading" class="default-margins">
    <CuratedGroupHeader />
    <AdmitDataWarning
      v-if="domain === 'admitted_students' && students && mode !== 'bulkAdd'"
      :updated-at="_get(students, '[0].updatedAt')"
    />
    <div v-show="mode !== 'bulkAdd'">
      <hr v-if="!error && totalStudentCount > itemsPerPage" class="filters-section-separator" />
      <div>
        <div class="d-flex flex-wrap justify-content-end pt-2">
          <div v-if="totalStudentCount && domain === 'default'">
            <TermSelector />
          </div>
          <div v-if="totalStudentCount > 1" class="pl-4">
            <SortBy :domain="domain" />
          </div>
        </div>
        <div v-if="totalStudentCount > itemsPerPage">
          <Pagination
            :click-handler="onClickPagination"
            :init-page-number="pageNumber"
            :limit="10"
            :per-page="itemsPerPage"
            :total-rows="totalStudentCount"
          />
        </div>
        <div v-if="_size(students)" class="mt-2">
          <div id="curated-cohort-students">
            <div v-if="domain === 'default'">
              <StudentRow
                v-for="(student, index) in students"
                :id="`student-${student.uid}`"
                :key="student.sid"
                class="border-bottom border-top pb-2 pt-3"
                :class="{'list-group-item-info': anchor === `#${student.uid}`}"
                :list-type="ownerId === currentUser.id ? 'curatedGroupForOwner' : 'curatedGroup'"
                :remove-student="removeStudent"
                :row-index="index"
                :sorted-by="currentUser.preferences.sortBy"
                :student="student"
                :term-id="currentUser.preferences.termId"
              />
            </div>
            <div v-if="domain === 'admitted_students'">
              <div class="pb-1">
                <hr class="filters-section-separator" />
              </div>
              <AdmitStudentsTable
                :include-curated-checkbox="false"
                :remove-student="removeStudent"
                :students="students"
              />
            </div>
          </div>
          <div v-if="totalStudentCount > itemsPerPage" class="mr-3">
            <Pagination
              :click-handler="onClickPagination"
              :init-page-number="pageNumber"
              :limit="10"
              :per-page="itemsPerPage"
              :total-rows="totalStudentCount"
            />
          </div>
        </div>
      </div>
    </div>
    <div v-if="!loading && mode === 'bulkAdd'" class="pt-2">
      <h2 class="page-section-header-sub my-2">Add {{ domain === 'admitted_students' ? 'Admits' : 'Students' }}</h2>
      <div class="w-75">
        <div>Type or paste a list of {{ domain === 'admitted_students' ? 'CS ID' : 'Student Identification (SID)' }} numbers numbers below.</div>
        <div class="text-medium-emphasis">Example: 9999999990, 9999999991</div>
      </div>
      <CuratedGroupBulkAdd
        :bulk-add-sids="bulkAddSids"
        :curated-group-id="curatedGroupId"
        :domain="domain"
      />
    </div>
  </div>
</template>

<script>
import AdmitDataWarning from '@/components/admit/AdmitDataWarning'
import AdmitStudentsTable from '@/components/admit/AdmitStudentsTable'
import Context from '@/mixins/Context'
import CuratedEditSession from '@/mixins/CuratedEditSession'
import CuratedGroupBulkAdd from '@/components/curated/CuratedGroupBulkAdd.vue'
import CuratedGroupHeader from '@/components/curated/CuratedGroupHeader'
import Pagination from '@/components/util/Pagination'
import SortBy from '@/components/student/SortBy'
import StudentRow from '@/components/student/StudentRow'
import TermSelector from '@/components/student/TermSelector'
import Util from '@/mixins/Util'
import {addStudentsToCuratedGroup, removeFromCuratedGroup} from '@/api/curated'
import {alertScreenReader, scrollTo, toInt} from '@/lib/utils'
import {describeCuratedGroupDomain, translateSortByOption} from '@/berkeley'
import {get} from 'lodash'
import {goToCuratedGroup} from '@/stores/curated-group/utils'
import {useContextStore} from '@/stores/context'
import {useCuratedGroupStore} from '@/stores/curated-group'
import {useRoute} from 'vue-router'

export default {
  name: 'CuratedGroup',
  components: {
    AdmitDataWarning,
    AdmitStudentsTable,
    CuratedGroupBulkAdd,
    CuratedGroupHeader,
    Pagination,
    SortBy,
    StudentRow,
    TermSelector
  },
  mixins: [Context, CuratedEditSession, Util],
  props: {
    id: {
      required: true,
      type: [String, Number]
    }
  },
  data: () => ({
    error: undefined
  }),
  computed: {
    anchor: () => location.hash
  },
  watch: {
    domain(newVal, oldVal) {
      this.removeEventHandler(`${oldVal === 'admitted_students' ? 'admitSortBy' : 'sortBy'}-user-preference-change`, this.onChangeSortBy)
      this.setEventHandler(`${newVal === 'admitted_students' ? 'admitSortBy' : 'sortBy'}-user-preference-change`, this.onChangeSortBy)
    }
  },
  created() {
    const curatedGroupId = toInt(get(useRoute(), 'params.id'))
    useCuratedGroupStore().resetMode()
    useCuratedGroupStore().setCuratedGroupId(parseInt(curatedGroupId))
    goToCuratedGroup(this.curatedGroupId, 1).then(group => {
      if (group) {
        this.loadingComplete(this.getLoadedAlert())
        this.setPageTitle(this.curatedGroupName)
        this.putFocusNextTick('curated-group-name')
      } else {
        this.$router.push({path: '/404'})
      }
    })
    const sortByKey = this.domain === 'admitted_students' ? 'admitSortBy' : 'sortBy'
    this.setEventHandler(`${sortByKey}-user-preference-change`, this.onChangeSortBy)
    this.setEventHandler('termId-user-preference-change', this.onChangeTerm)
  },
  unmounted() {
    const sortByKey = this.domain === 'admitted_students' ? 'admitSortBy' : 'sortBy'
    this.removeEventHandler(`${sortByKey}-user-preference-change`, this.onChangeSortBy)
    this.removeEventHandler('termId-user-preference-change', this.onChangeTerm)
  },
  mounted() {
    this.nextTick(function() {
      if (!location.hash) {
        return false
      }
      let anchor = this.anchor.replace(/(#)([0-9])/g, function(a, m1, m2) {
        return `${m1}student-${m2}`
      })
      scrollTo(anchor)
    })
  },
  methods: {
    bulkAddSids(sids) {
      useCuratedGroupStore().resetMode()
      if (this._size(sids)) {
        alertScreenReader(`Adding ${sids.length} students`)
        useContextStore().updateCurrentUserPreference('sortBy', 'last_name')
        addStudentsToCuratedGroup(this.curatedGroupId, sids, true).then(() => {
          goToCuratedGroup(this.curatedGroupId, 1).then(() => {
            this.loadingComplete(`${sids.length} students added to group '${this.name}'`)
            this.putFocusNextTick('curated-group-name')
          })
        })
      } else {
        alertScreenReader('Canceled bulk add of students')
        this.putFocusNextTick('curated-group-name')
      }
    },
    getLoadedAlert() {
      const label = `${this._capitalize(describeCuratedGroupDomain(this.domain))} ${this.curatedGroupName || ''}`
      const sortedBy = translateSortByOption(this.currentUser.preferences.sortBy)
      return `${label}, sorted by ${sortedBy}, ${this.pageNumber > 1 ? `(page ${this.pageNumber})` : ''} has loaded`
    },
    onChangeSortBy() {
      if (!this.loading) {
        this.loadingStart()
        goToCuratedGroup(this.curatedGroupId, 1).then(() => {
          this.loadingComplete(this.getLoadedAlert())
        })
      }
    },
    onChangeTerm() {
      if (!this.loading) {
        this.loadingStart()
        goToCuratedGroup(this.curatedGroupId, this.pageNumber).then(() => {
          this.loadingComplete(this.getLoadedAlert())
        })
      }
    },
    onClickPagination(pageNumber) {
      this.loadingStart()
      goToCuratedGroup(this.curatedGroupId, pageNumber).then(() => {
        this.loadingComplete(this.getLoadedAlert())
      })
    },
    removeStudent(sid) {
      useCuratedGroupStore().removeStudent(sid)
      return removeFromCuratedGroup(this.curatedGroupId, sid).then(group => {
        useCuratedGroupStore().setTotalStudentCount(group.totalStudentCount)
      })
    }
  }
}
</script>
