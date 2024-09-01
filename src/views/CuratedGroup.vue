<template>
  <div v-if="!contextStore.loading" class="default-margins">
    <CuratedGroupHeader />
    <div v-if="domain === 'admitted_students' && students && mode !== 'bulkAdd'" class="mt-2">
      <AdmitDataWarning :updated-at="get(students, '[0].updatedAt')" />
    </div>
    <div v-if="mode !== 'bulkAdd'">
      <hr v-if="!error && totalStudentCount > itemsPerPage" class="filters-section-separator" />
      <div>
        <div class="d-flex flex-wrap justify-end mt-3">
          <div v-if="totalStudentCount && domain === 'default'" class="mr-3">
            <TermSelector />
          </div>
          <div v-if="totalStudentCount > 1">
            <SortBy :domain="domain" />
          </div>
        </div>
        <div v-if="totalStudentCount > itemsPerPage" class="mt-2">
          <Pagination
            :click-handler="onClickPagination"
            :init-page-number="pageNumber"
            :limit="10"
            :per-page="itemsPerPage"
            :total-rows="totalStudentCount"
          />
        </div>
        <div v-if="size(students)" class="mt-2">
          <div id="curated-cohort-students">
            <div v-if="domain === 'default'">
              <StudentRow
                v-for="(student, index) in students"
                :id="`student-${student.uid}`"
                :key="student.sid"
                class="border-bottom border-top pb-2 pt-3"
                :class="{'list-group-item-info': anchor === `#${student.uid}`}"
                :list-type="curatedStore.ownerId === currentUser.id ? 'curatedGroupForOwner' : 'curatedGroup'"
                :remove-student="removeStudent"
                :row-index="index"
                :sorted-by="currentUser.preferences.sortBy"
                :student="student"
                :term-id="currentUser.preferences.termId"
              />
            </div>
            <div v-if="domain === 'admitted_students'">
              <hr />
              <AdmitStudentsTable
                :include-curated-checkbox="false"
                :remove-student="removeStudent"
                :students="students"
              />
            </div>
          </div>
          <div v-if="totalStudentCount > itemsPerPage" class="mr-3 mt-7">
            <Pagination
              :click-handler="onClickPagination"
              id-prefix="auxiliary-pagination"
              :init-page-number="pageNumber"
              :limit="10"
              :per-page="itemsPerPage"
              :total-rows="totalStudentCount"
            />
          </div>
        </div>
      </div>
    </div>
    <div v-if="!contextStore.loading && mode === 'bulkAdd'" class="pt-2">
      <h2 id="page-section-header" class="page-section-header-sub my-2">
        Add {{ domain === 'admitted_students' ? 'Admits' : 'Students' }}
      </h2>
      <div id="page-description" class="w-75">
        <div>Type or paste a list of {{ domain === 'admitted_students' ? 'CS ID' : 'Student Identification (SID)' }} numbers numbers below.</div>
        <div class="text-medium-emphasis">Example: 9999999990, 9999999991</div>
      </div>
      <CuratedGroupBulkAdd
        :bulk-add-sids="bulkAddSids"
        :curated-group-id="curatedGroupId"
        :domain="domain"
        :is-saving="isAddingStudents"
      />
    </div>
  </div>
</template>

<script setup>
import AdmitDataWarning from '@/components/admit/AdmitDataWarning'
import AdmitStudentsTable from '@/components/admit/AdmitStudentsTable'
import CuratedGroupBulkAdd from '@/components/curated/CuratedGroupBulkAdd'
import CuratedGroupHeader from '@/components/curated/CuratedGroupHeader'
import Pagination from '@/components/util/Pagination'
import router from '@/router'
import SortBy from '@/components/student/SortBy'
import StudentRow from '@/components/student/StudentRow'
import TermSelector from '@/components/student/TermSelector'
import {addStudentsToCuratedGroup, removeFromCuratedGroup} from '@/api/curated'
import {alertScreenReader, putFocusNextTick, scrollTo, setPageTitle, toInt} from '@/lib/utils'
import {describeCuratedGroupDomain, translateSortByOption} from '@/berkeley'
import {capitalize, get, size} from 'lodash'
import {goToCuratedGroup} from '@/stores/curated-group/utils'
import {useContextStore} from '@/stores/context'
import {useCuratedGroupStore} from '@/stores/curated-group'
import {useRoute} from 'vue-router'
import {computed, nextTick, onMounted, onUnmounted, ref, watch} from 'vue'
import {storeToRefs} from 'pinia'

defineProps({
  id: {
    required: true,
    type: [String, Number]
  }
})

const anchor = computed(() => location.hash)
const contextStore = useContextStore()
const curatedStore = useCuratedGroupStore()
const currentUser = contextStore.currentUser
const error = ref(undefined)
const isAddingStudents = ref(false)
const {curatedGroupId, domain, itemsPerPage, mode, pageNumber, students, totalStudentCount} = storeToRefs(curatedStore)

watch(() => curatedStore.domain, (newVal, oldVal) => {
  contextStore.removeEventHandler(`${oldVal === 'admitted_students' ? 'admitSortBy' : 'sortBy'}-user-preference-change`, onChangeSortBy)
  contextStore.setEventHandler(`${newVal === 'admitted_students' ? 'admitSortBy' : 'sortBy'}-user-preference-change`, onChangeSortBy)
})

contextStore.loadingStart()

onMounted(() => {
  const idParam = toInt(get(useRoute(), 'params.id'))
  curatedStore.resetMode()
  curatedStore.setCuratedGroupId(parseInt(idParam))
  goToCuratedGroup(curatedStore.curatedGroupId, 1).then(group => {
    if (group) {
      contextStore.loadingComplete(getLoadedAlert())
      setPageTitle(curatedStore.curatedGroupName)
      putFocusNextTick('curated-group-name')
    } else {
      router.push({path: '/404'})
    }
  })
  const sortByKey = domain.value === 'admitted_students' ? 'admitSortBy' : 'sortBy'
  contextStore.setEventHandler(`${sortByKey}-user-preference-change`, onChangeSortBy)
  contextStore.setEventHandler('termId-user-preference-change', onChangeTerm)
  nextTick(() => {
    if (!location.hash) {
      return false
    }
    scrollTo(anchor.value.replace(/(#)([0-9])/g, (a, m1, m2) => `${m1}student-${m2}`))
  })
})

onUnmounted(() => {
  const sortByKey = domain.value === 'admitted_students' ? 'admitSortBy' : 'sortBy'
  contextStore.removeEventHandler(`${sortByKey}-user-preference-change`, onChangeSortBy)
  contextStore.removeEventHandler('termId-user-preference-change', onChangeTerm)
})

const bulkAddSids = sids => {
  if (size(sids)) {
    isAddingStudents.value = true
    alertScreenReader(`Adding ${sids.length} students`)
    contextStore.updateCurrentUserPreference('sortBy', 'last_name')
    addStudentsToCuratedGroup(curatedGroupId.value, sids, true).then(() => {
      goToCuratedGroup(curatedGroupId.value, 1).then(() => {
        curatedStore.resetMode()
        isAddingStudents.value = false
        putFocusNextTick('curated-group-name')
      })
    })
  } else {
    curatedStore.resetMode()
    alertScreenReader('Canceled bulk add of students')
    putFocusNextTick('curated-group-name')
  }
}

const getLoadedAlert = () => {
  const label = `${capitalize(describeCuratedGroupDomain(domain.value))} ${curatedStore.curatedGroupName || ''}`
  const sortedBy = translateSortByOption(currentUser.preferences.sortBy)
  return `${label}, sorted by ${sortedBy}, ${pageNumber.value > 1 ? `(page ${pageNumber.value})` : ''} has loaded`
}

const onChangeSortBy = () => {
  if (!contextStore.loading) {
    contextStore.loadingStart()
    goToCuratedGroup(curatedGroupId.value, 1).then(() => {
      contextStore.loadingComplete(getLoadedAlert())
    })
  }
}

const onChangeTerm = () => {
  if (!contextStore.loading) {
    contextStore.loadingStart()
    goToCuratedGroup(curatedGroupId.value, pageNumber.value).then(() => {
      contextStore.loadingComplete(getLoadedAlert())
    })
  }
}

const onClickPagination = pageNumber => {
  contextStore.loadingStart()
  goToCuratedGroup(curatedGroupId.value, pageNumber).then(() => {
    contextStore.loadingComplete(getLoadedAlert())
  })
}

const removeStudent = sid => {
  curatedStore.removeStudent(sid)
  return removeFromCuratedGroup(curatedGroupId.value, sid).then(data => {
    curatedStore.setTotalStudentCount(data.totalStudentCount)
  })
}
</script>
