<template>
  <div class="course d-flex flex-column position-relative" :class="{'course-expanded': showCourseDetails}">
    <div
      :id="baseElementId"
      class="align-center course-row d-flex"
      role="row"
    >
      <div role="cell" class="column-name" :class="{'': showCourseDetails}">
        <v-btn
          :id="`${baseElementId}-toggle`"
          :aria-expanded="showCourseDetails ? 'true' : 'false'"
          :aria-controls="`${baseElementId}-details`"
          class="align-center d-flex font-weight-bold font-size-16 pl-0"
          color="primary"
          density="compact"
          variant="text"
          @click="toggleShowCourseDetails"
        >
          <v-icon :icon="showCourseDetails ? mdiMenuDown : mdiMenuRight" />
          <span class="sr-only">{{ showCourseDetails ? 'Hide' : 'Show' }} {{ course.displayName }} class details for {{ student.name }}</span>
          <div
            :id="`${baseElementId}-name`"
            class="course-name overflow-hidden text-left truncate-with-ellipsis"
            :class="{'demo-mode-blur': currentUser.inDemoMode}"
          >
            {{ course.displayName }}
          </div>
        </v-btn>
        <div
          v-if="course.waitlisted"
          :id="`waitlisted-for-${termId}-${course.sections.length ? course.sections[0].ccn : course.displayName}`"
          class="font-size-12 font-weight-black ml-5 text-error text-uppercase"
        >
          Waitlisted
        </div>
      </div>
      <div class="align-center column-grade d-flex pl-1 text-nowrap" role="cell">
        <span
          v-if="course.midtermGrade"
          :id="`${baseElementId}-midterm-grade`"
          v-accessible-grade="course.midtermGrade"
        />
        <span
          v-if="!course.midtermGrade"
          :id="`${baseElementId}-midterm-grade`"
        ><span class="sr-only">No data</span>&mdash;</span>
        <v-icon
          v-if="isAlertGrade(course.midtermGrade) && !course.grade"
          :id="`${baseElementId}-has-midterm-grade-alert`"
          :icon="mdiAlertRhombus"
          class="warning"
        />
      </div>
      <div class="align-center column-grade d-flex text-nowrap" role="cell">
        <span
          v-if="course.grade"
          :id="`${baseElementId}-final-grade`"
          v-accessible-grade="course.grade"
        />
        <span
          v-if="!course.grade"
          :id="`${baseElementId}-final-grade`"
          class="font-italic text-medium-emphasis"
        >{{ course.gradingBasis }}</span>
        <v-icon
          v-if="isAlertGrade(course.grade)"
          :id="`${baseElementId}-has-grade-alert`"
          class="warning ml-1"
          color="warning"
          :icon="mdiAlert"
        />
        <IncompleteGradeAlertIcon
          v-if="sectionsWithIncompleteStatus.length"
          :course="course"
          :index="index"
          :term-id="termId"
        />
        <span v-if="!course.grade && !course.gradingBasis" :id="`${baseElementId}-final-grade`"><span class="sr-only">No data</span>&mdash;</span>
      </div>
      <div class="column-units font-size-14 pl-1 pt-1 text-nowrap text-right" role="cell">
        <span :id="`${baseElementId}-units`">{{ numeral(course.units).format('0.0') }}</span>
      </div>
    </div>
    <v-expand-transition
      :id="`course-details-${year}-${termId}-${index}`"
      class="course-details"
      :class="{
        'align-self-start': columnIndex === 0,
        'align-self-center': columnIndex === 1,
        'align-self-end': columnIndex === 2
      }"
    >
      <div v-if="showCourseDetails">
        <div
          :id="`${baseElementId}-details-name`"
          class="font-size-16 font-weight-bold text-medium-emphasis"
          :class="{'demo-mode-blur': currentUser.inDemoMode}"
        >
          {{ course.displayName }}
        </div>
        <div class="d-inline-block font-size-14 font-weight-regular mt-1 text-no-wrap">
          <span
            v-for="(section, sectionIndex) in course.sections"
            :key="sectionIndex"
          >
            <span v-if="section.displayName" :class="{'demo-mode-blur': currentUser.inDemoMode}">
              <span v-if="sectionIndex === 0"></span><!--
                --><router-link
                v-if="section.isViewableOnCoursePage"
                :id="`term-${termId}-section-${section.ccn}`"
                :to="`/course/${termId}/${section.ccn}?u=${student.uid}`"
                class="font-weight-black"
                :class="{'demo-mode-blur': currentUser.inDemoMode}"
              ><span class="sr-only">Link to {{ course.displayName }}, </span>{{ section.displayName }}</router-link><!--
                --><span v-if="!section.isViewableOnCoursePage">{{ section.displayName }}</span><!--
                --><span v-if="sectionIndex < course.sections.length - 1"> | </span><!--
                --><span v-if="sectionIndex === course.sections.length - 1"></span>
            </span>
          </span>
        </div>
        <div :id="`${baseElementId}-title`" :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ course.title }}</div>
        <div v-if="course.courseRequirements">
          <div v-for="requirement in course.courseRequirements" :key="requirement" class="d-flex align-center font-size-14 text-no-wrap">
            <v-icon class="text-warning pr-1" :icon="mdiStar" /> {{ requirement }}
          </div>
        </div>
        <StudentCourseCanvasData
          v-if="currentUser.canAccessCanvasData"
          :course="course"
          :index="index"
          :student="student"
          :term="term"
        />
        <div
          v-for="section in sectionsWithIncompleteStatus"
          :key="section.ccn"
          class="align-items-center d-flex pb-2"
        >
          <v-chip
            class="align-center d-flex font-size-12 font-weight-black mr-2 text-uppercase text-nowrap"
            color="error"
            density="compact"
            :prepend-icon="mdiInformationSlabBox"
            size="small"
            text="Incomplete Grade"
            variant="flat"
          />
          <div :id="`term-${termId}-section-${section.ccn}-has-incomplete-grade`" class="font-size-14">
            {{ sectionsWithIncompleteStatus.length > 1 ? `${section.displayName} :` : '' }}
            {{ getIncompleteGradeDescription(course.displayName, [section]) }}
          </div>
        </div>
      </div>
    </v-expand-transition>
    <v-spacer
      v-if="showSpacer"
      :id="`spacer-${year}-${termId}-${index}`"
    >
      &nbsp;
    </v-spacer>
  </div>
</template>

<script setup>
import IncompleteGradeAlertIcon from '@/components/student/IncompleteGradeAlertIcon'
import numeral from 'numeral'
import StudentCourseCanvasData from '@/components/student/profile/StudentCourseCanvasData'
import {get, size} from 'lodash'
import {
  getIncompleteGradeDescription,
  getSectionsWithIncompleteStatus,
  isAlertGrade,
} from '@/berkeley'
import {mdiAlert, mdiAlertRhombus, mdiInformationSlabBox, mdiMenuDown, mdiMenuRight, mdiStar} from '@mdi/js'
import {nextTick, onMounted, onUnmounted, ref} from 'vue'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  columnIndex: {
    required: true,
    type: Number
  },
  course: {
    required: true,
    type: Object
  },
  index: {
    required: true,
    type: Number
  },
  student: {
    required: true,
    type: Object
  },
  term: {
    required: true,
    type: Object
  },
  year: {
    required: true,
    type: String
  }
})

const contextStore = useContextStore()

const baseElementId = `term-${props.term.termId}-course-${get(props.course, 'sections[0].ccn')}`
const currentUser = contextStore.currentUser
const sectionsWithIncompleteStatus = ref(getSectionsWithIncompleteStatus(props.course.sections))
const showCourseDetails = ref(false)
const showSpacer = ref(false)
const termId = props.term.termId
const toggleEventName = `student-${props.student.uid}`

onMounted(() => {
  contextStore.setEventHandler(toggleEventName, clicked => {
    showSpacer.value = false
    const isOtherCourse = clicked.index !== props.index || clicked.termId !== termId || clicked.year !== props.year
    if (isOtherCourse) {
      showCourseDetails.value = false
      const isHorizontallyAligned = clicked.index === props.index && clicked.year === props.year
      const isClickedElementDownUnder = clicked.year === props.year
        && clicked.termId !== termId
        && clicked.index > props.index
        && props.index === size(props.term.enrollments) - 1
      if (clicked.show && (isHorizontallyAligned || isClickedElementDownUnder)) {
        showSpacer.value = true
        // User just clicked to view details of some other course.
        nextTick(() => {
          const clickedElementId = `course-details-${clicked.year}-${clicked.termId}-${clicked.index}`
          const observer = new ResizeObserver(() => {
            const e = document.getElementById(clickedElementId)
            if (e) {
              nextTick(() => {
                const spacerId = `spacer-${props.year}-${termId}-${props.index}`
                const spacer = document.getElementById(spacerId)
                if (spacer) {
                  // TODO: Hard-coded value below should be computed more intelligently.
                  const height = isClickedElementDownUnder ? 300 : e.offsetHeight
                  spacer.setAttribute('style', `height: ${height}px`)
                }
              })
            }
          })
          observer.observe(document.getElementById(clickedElementId))
        })
      }
    }
  })
})

onUnmounted(() => {
  showCourseDetails.value = false
  showSpacer.value = false
  contextStore.removeEventHandler(toggleEventName)
})

const toggleShowCourseDetails = () => {
  const show = !showCourseDetails.value
  showCourseDetails.value = show
  showSpacer.value = false
  const clicked = {
    index: props.index,
    show,
    termId,
    year: props.year
  }
  contextStore.broadcast(toggleEventName, clicked)
}
</script>

<style scoped>
@media (min-width: 1200px) {
  .course-details {
    border: 1px rgba(var(--v-border-color), var(--v-border-opacity)) solid;
    margin: 0 -11px;
    width: 332% !important;
  }
  .course-expanded {
    border-bottom: 0 !important;
  }
}
.column-grade {
  width: 15%;
}
.column-name {
  width: 60%;
}
.column-units {
  width: 15%;
}
.course {
  padding: 3px 10px 0 !important;
  position: relative;
}
.course-details {
  background-color: rgb(var(--v-theme-pale-blue));
  padding: 10px 0 10px 20px;
  position: relative;
  top: -1px;
  width: 100%;
  z-index: 1;
}
.course-expanded {
  background-color: rgb(var(--v-theme-pale-blue));
  border: 1px rgba(var(--v-border-color), var(--v-border-opacity)) solid;
}
.course-expanded .course-row {
  background-color: rgb(var(--v-theme-pale-blue));
  z-index: 2;
}
.course-name {
  height: 1.1em;
  line-height: 1.1;
  max-width: 90%;
  overflow: hidden;
}
.course-row {
  height: 2.2em;
  line-height: 1.1;
  margin: 0 -10px;
  overflow-wrap: break-word;
  padding: 0 8px 0 0;
}
</style>
