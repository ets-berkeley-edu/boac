<template>
  <div class="m-3">
    <Spinner />
    <div v-if="!loading">
      <CuratedGroupHeader />
      <AdmitDataWarning
        v-if="domain === 'admitted_students' && students && mode !== 'bulkAdd'"
        :updated-at="$_.get(students, '[0].updatedAt')"
      />
      <div v-show="mode !== 'bulkAdd'">
        <hr v-if="!error && totalStudentCount > itemsPerPage" class="filters-section-separator" />
        <div>
          <div class="d-flex justify-content-end pt-2">
            <div v-if="totalStudentCount && domain === 'default'" class="pr-4">
              <TermSelector />
            </div>
            <div v-if="totalStudentCount > 1">
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
          <div v-if="$_.size(students)" class="mt-2">
            <div id="curated-cohort-students">
              <div v-if="domain === 'default'">
                <StudentRow
                  v-for="(student, index) in students"
                  :id="`student-${student.uid}`"
                  :key="student.sid"
                  class="border-bottom border-top pb-2 pt-3"
                  :class="{'list-group-item-info': anchor === `#${student.uid}`}"
                  :list-type="ownerId === $currentUser.id ? 'curatedGroupForOwner' : 'curatedGroup'"
                  :remove-student="removeStudent"
                  :row-index="index"
                  :sorted-by="$currentUser.preferences.sortBy"
                  :student="student"
                  :term-id="$currentUser.preferences.termId"
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
        <h2 class="page-section-header-sub my-2">Add {{ domain ? 'Admits' : 'Students' }}</h2>
        <div class="w-75">
          <div>Type or paste a list of {{ domain === 'admitted_students' ? 'CS ID' : 'Student Identification (SID)' }} numbers numbers below.</div>
          <div class="text-secondary">Example: 9999999990, 9999999991</div>
        </div>
        <CuratedGroupBulkAdd
          :bulk-add-sids="bulkAddSids"
          :curated-group-id="curatedGroupId"
          :domain="domain"
        />
      </div>
    </div>
  </div>
</template>

<script>
import AdmitDataWarning from '@/components/admit/AdmitDataWarning'
import AdmitStudentsTable from '@/components/admit/AdmitStudentsTable'
import Berkeley from '@/mixins/Berkeley'
import Context from '@/mixins/Context'
import CuratedGroupBulkAdd from '@/components/curated/CuratedGroupBulkAdd.vue'
import CuratedEditSession from '@/mixins/CuratedEditSession'
import CuratedGroupHeader from '@/components/curated/CuratedGroupHeader'
import Loading from '@/mixins/Loading'
import Pagination from '@/components/util/Pagination'
import Scrollable from '@/mixins/Scrollable'
import SortBy from '@/components/student/SortBy'
import Spinner from '@/components/util/Spinner'
import TermSelector from '@/components/student/TermSelector'
import StudentRow from '@/components/student/StudentRow'
import Util from '@/mixins/Util'

export default {
  name: 'CuratedGroup',
  components: {
    AdmitDataWarning,
    AdmitStudentsTable,
    CuratedGroupBulkAdd,
    CuratedGroupHeader,
    Pagination,
    SortBy,
    Spinner,
    StudentRow,
    TermSelector
  },
  mixins: [Berkeley, Context, CuratedEditSession, Loading, Scrollable, Util],
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
  created() {
    this.setMode(undefined)
    this.init(parseInt(this.id)).then(group => {
      if (group) {
        this.loaded(this.getLoadedAlert())
        this.setPageTitle(this.curatedGroupName)
        this.$putFocusNextTick('curated-group-name')
        if (this.pageNumber > 1) {
          this.$ga.curatedEvent(this.curatedGroupId, this.curatedGroupName, 'view')
        }
      } else {
        this.$router.push({path: '/404'})
      }
    })
    const sortByKey = this.domain === 'admitted_students' ? 'admitSortBy' : 'sortBy'
    const eventName = `${sortByKey}-user-preference-change`
    this.$eventHub.off(eventName)
    this.$eventHub.on(eventName, sortBy => {
      if (!this.loading) {
        this.loadingStart()
        this.$announcer.polite(`Sorting students by ${sortBy}`)
        this.goToPage(1).then(() => {
          this.loaded(this.getLoadedAlert())
          this.$ga.curatedEvent(this.curatedGroupId, this.curatedGroupName, `sort by ${sortBy}`)
        })
      }
    })
    this.$eventHub.on('termId-user-preference-change', termId => {
      if (!this.loading) {
        this.loadingStart()
        this.goToPage(this.pageNumber).then(() => {
          this.loaded(this.getLoadedAlert())
          this.$ga.curatedEvent(this.curatedGroupId, this.curatedGroupName, `Term id changed to ${termId}`)
        })
      }
    })
  },
  mounted() {
    this.$nextTick(function() {
      if (!this.anchor) {
        return false
      }
      let anchor = this.anchor.replace(/(#)([0-9])/g, function(a, m1, m2) {
        return `${m1}student-${m2}`
      })
      this.scrollTo(anchor)
    })
  },
  methods: {
    bulkAddSids(sids) {
      this.setMode(undefined)
      if (this.$_.size(sids)) {
        this.$announcer.polite(`Adding ${sids.length} students`)
        this.$currentUser.preferences.sortBy = 'last_name'
        this.loadingStart()
        this.addStudents(sids).then(() => {
          this.loaded(this.getLoadedAlert())
          this.$putFocusNextTick('curated-group-name')
          this.$announcer.polite(`${sids.length} students added to group '${this.name}'`)
          const domainLabel = this.describeCuratedGroupDomain(this.domain)
          this.$ga.curatedEvent(this.curatedGroupId, this.curatedGroupName, `Update ${domainLabel} with bulk-add SIDs`)
        })
      } else {
        this.$announcer.polite('Canceled bulk add of students')
        this.$putFocusNextTick('curated-group-name')
      }
    },
    getLoadedAlert() {
      const label = `${this.$_.capitalize(this.describeCuratedGroupDomain(this.domain))} ${this.curatedGroupName || ''}`
      const sortedBy = this.translateSortByOption(this.$currentUser.preferences.sortBy)
      return `${label}, sorted by ${sortedBy}, ${this.pageNumber > 1 ? `(page ${this.pageNumber})` : ''} has loaded`
    },
    onClickPagination(pageNumber) {
      this.loadingStart()
      this.goToPage(pageNumber).then(() => {
        this.loaded(this.getLoadedAlert())
        this.$ga.curatedEvent(this.curatedGroupId, this.curatedGroupName, `Page ${pageNumber}`)
      })
    }
  }
}
</script>

<style scoped>
h3 {
  color: #666;
  font-size: 18px;
}
</style>
