<template>
  <div v-if="!contextStore.loading" class="default-margins">
    <CuratedGroupHeader />
    <div v-if="domain === 'admitted_students' && students && mode !== 'bulkAdd'" class="pt-2">
      <AdmitDataWarning :updated-at="get(students, '[0].updatedAt')" />
    </div>
    <div v-if="mode !== 'bulkAdd'">
      <div class="align-start d-flex flex-wrap w-100">
        <div class="ml-auto py-1">
          <TermSelector
            v-if="totalStudentCount && domain === 'default'"
            class="py-1"
            label-class="cohort-sort-by-label"
            select-class="cohort-sort-by-select"
          />
          <SortBy
            v-if="totalStudentCount > 1"
            class="py-1"
            :domain="domain"
            label-class="cohort-sort-by-label"
            select-class="cohort-sort-by-select"
          />
        </div>
      </div>
      <div class="align-self-end mr-auto py-1">
        <Pagination
          v-if="totalStudentCount > itemsPerPage"
          :click-handler="goToPage"
          :init-page-number="pageNumber"
          :limit="10"
          :per-page="itemsPerPage"
          :total-rows="totalStudentCount"
        />
      </div>
      <div v-if="size(students)">
        <div id="curated-cohort-students" class="scroll-margins" tabindex="-1">
          <v-container v-if="domain === 'default'" class="pl-1" fluid>
            <StudentRow
              v-for="(student, index) in students"
              :id="`student-${student.uid}`"
              :key="student.sid"
              class="border-b-sm border-t-sm pb-2 pt-3"
              :class="{'list-group-item-info': anchor === `#${student.uid}`}"
              :list-type="curatedStore.owner.id === currentUser.id ? 'curatedGroupForOwner' : 'curatedGroup'"
              :remove-student="() => removeStudent(student)"
              :row-index="index"
              :sorted-by="currentUser.preferences.sortBy"
              :student="student"
              :term-id="currentUser.preferences.termId"
            />
          </v-container>
          <div v-if="domain === 'admitted_students'">
            <hr>
            <AdmitStudentsTable
              :include-curated-checkbox="false"
              :remove-student="removeStudent"
              :students="students"
            />
          </div>
        </div>
        <div v-if="totalStudentCount > itemsPerPage" class="pr-3 pt-7">
          <Pagination
            :click-handler="goToPage"
            id-prefix="auxiliary-pagination"
            :init-page-number="pageNumber"
            :is-widget-at-bottom-of-page="true"
            :limit="10"
            :per-page="itemsPerPage"
            :total-rows="totalStudentCount"
          />
        </div>
      </div>
    </div>
    <div v-if="!contextStore.loading && mode === 'bulkAdd'" class="pt-2">
      <h2 id="page-section-header" class="page-section-header-sub my-2">
        Add {{ domain === 'admitted_students' ? 'Admits' : 'Students' }} to {{ describeCuratedGroupDomain(domain, true) }}
      </h2>
      <CuratedGroupBulkAdd
        :bulk-add-sids="bulkAddSids"
        :curated-group-id="curatedGroupId"
        :domain="domain"
        heading-id="page-section-header"
        :is-saving="isAddingStudents"
      />
    </div>
  </div>
</template>

<script lang="ts" setup>
import {get, multiply, size, toString} from 'lodash'
import {computed, nextTick, onMounted, onUnmounted, ref, watch} from 'vue'
import {storeToRefs} from 'pinia'
import {useRoute, useRouter} from 'vue-router'
import AdmitDataWarning from '@/components/admit/AdmitDataWarning.vue'
import AdmitStudentsTable from '@/components/admit/AdmitStudentsTable.vue'
import CuratedGroupBulkAdd from '@/components/curated/CuratedGroupBulkAdd.vue'
import CuratedGroupHeader from '@/components/curated/CuratedGroupHeader.vue'
import Pagination from '@/components/util/Pagination.vue'
import SortBy from '@/components/student/SortBy.vue'
import StudentRow from '@/components/student/StudentRow.vue'
import TermSelector from '@/components/student/TermSelector.vue'
import {addStudentsToCuratedGroups, getCuratedGroup, removeFromCuratedGroups} from '@/api/curated'
import {alertScreenReader, pluralize, putFocusNextTick, scrollTo, setPageTitle, toInt} from '@/lib/utils'
import {describeCuratedGroupDomain} from '@/lib/berkeley-utils'
import {useContextStore} from '@/stores/context'
import {useCuratedGroupStore} from '@/stores/curated-group'

const anchor = computed(() => location.hash)
const contextStore = useContextStore()
const curatedStore = useCuratedGroupStore()
const currentUser = contextStore.currentUser
const isAddingStudents = ref(false)
const router = useRouter()
const sortByKey = computed<string>(() => domain.value === 'admitted_students' ? 'admitSortBy' : 'sortBy')
const {curatedGroupId, domain, itemsPerPage, mode, pageNumber, students, totalStudentCount} = storeToRefs(curatedStore)


watch(() => curatedStore.domain, (newVal, oldVal) => {
  contextStore.removeEventHandler(`${oldVal === 'admitted_students' ? 'admitSortBy' : 'sortBy'}-user-preference-change`, onChangeSortBy)
  contextStore.setEventHandler(`${newVal === 'admitted_students' ? 'admitSortBy' : 'sortBy'}-user-preference-change`, onChangeSortBy)
})

contextStore.loadingStart()

onMounted(() => {
  const idParam: number = toInt(toString(useRoute().params.id))
  curatedStore.resetMode()
  curatedStore.setCuratedGroupId(idParam)
  fetchCuratedGroup(curatedStore.curatedGroupId, 1).then(group => {
    if (group) {
      setPageTitle(curatedStore.curatedGroupName)
      contextStore.loadingComplete('curated-group-name')
    } else {
      router.push({path: '/404'})
    }
  })
  contextStore.setEventHandler(`${sortByKey.value}-user-preference-change`, onChangeSortBy)
  contextStore.setEventHandler('termId-user-preference-change', onChangeTerm)
  nextTick(() => {
    if (!location.hash) {
      return false
    }
    scrollTo(anchor.value.replace(/(#)([0-9])/g, (a, m1, m2) => `${m1}student-${m2}`))
  })
})

onUnmounted(() => {
  contextStore.removeEventHandler(`${sortByKey.value}-user-preference-change`, onChangeSortBy)
  contextStore.removeEventHandler('termId-user-preference-change', onChangeTerm)
})

const bulkAddSids = sids => {
  if (size(sids)) {
    isAddingStudents.value = true
    alertScreenReader(`Adding ${pluralize('student', sids.length)} to ${describeCuratedGroupDomain(domain.value)}`)
    contextStore.updateCurrentUserPreference('sortBy', 'last_name')
    addStudentsToCuratedGroups([curatedGroupId.value], sids, true).then(() => {
      fetchCuratedGroup(curatedGroupId.value, 1).then(() => {
        curatedStore.resetMode()
        isAddingStudents.value = false
        putFocusNextTick('bulk-add-sids-button')
      })
    })
  } else {
    curatedStore.resetMode()
    alertScreenReader(`Canceled add students to ${describeCuratedGroupDomain(domain.value)}`)
    putFocusNextTick('bulk-add-sids-button')
  }
}

const fetchCuratedGroup = (curatedGroupId: number, pageNumber: number) => {
  return new Promise(resolve => {
    const domain = curatedStore.domain
    const itemsPerPage = curatedStore.itemsPerPage
    const offset: number = multiply(pageNumber - 1, itemsPerPage)
    const orderBy: string = get(currentUser.preferences, domain === 'admitted_students' ? 'admitSortBy' : 'sortBy', 'sortBy')
    getCuratedGroup(
      curatedGroupId,
      itemsPerPage,
      offset,
      orderBy,
      currentUser.preferences.termId
    ).then(group => {
      curatedStore.setCuratedGroupName(group.name)
      curatedStore.setDomain(group.domain)
      curatedStore.setOwner({
        id: group.ownerId,
        deptCodes: group.ownerDeptCodes || [],
        name: group.ownerName || undefined,
        uid: group.ownerUid
      })
      curatedStore.setReferencingCohortIds(group.referencingCohortIds)
      curatedStore.setStudents(group.students)
      curatedStore.setTotalStudentCount(group.totalStudentCount)
      resolve(group)
    })
  })
}

const goToPage = page => {
  return new Promise<void>(resolve => {
    curatedStore.setPageNumber(page)
    contextStore.loadingStart()
    fetchCuratedGroup(curatedGroupId.value, page).then(() => {
      contextStore.loadingComplete()
      resolve()
    })
  })
}
const onChangeSortBy = () => {
  if (!contextStore.loading) {
    contextStore.loadingStart()
    fetchCuratedGroup(curatedGroupId.value, 1).then(() => {
      nextTick(() => putFocusNextTick('students-sort-by'))
      contextStore.loadingComplete()
    })
  }
}

const onChangeTerm = () => {
  if (!contextStore.loading) {
    contextStore.loadingStart()
    fetchCuratedGroup(curatedGroupId.value, pageNumber.value ? pageNumber.value : 1).then(() => {
      nextTick(() => putFocusNextTick('students-term-select'))
      contextStore.loadingComplete()
    })
  }
}

const removeStudent = student => {
  curatedStore.removeStudent(student.sid)
  removeFromCuratedGroups([curatedGroupId.value], student.sid).then(() => {
    fetchCuratedGroup(curatedGroupId.value, 1).then(() => {
      curatedStore.resetMode()
    })
  })
  alertScreenReader(`Removed ${student.firstName} ${student.lastName} from group`)
}
</script>
