<template>
  <div :class="{'cursor-grabbing': degreeStore.draggingContext.course}" @drag="scrollTo">
    <div v-if="!loading">
      <div class="border-bottom bg-sky-blue">
        <StudentProfileHeader
          :compact="true"
          :link-to-student-profile="true"
          :student="student"
        />
      </div>
      <StudentDegreeCheckHeader :student="student" />
      <v-container class="pt-3" fluid>
        <v-row>
          <v-col :cols="$vuetify.display.mdAndUp ? 4 : 12">
            <UnitRequirements class="unit-requirements" />
          </v-col>
          <v-col :cols="$vuetify.display.mdAndUp ? (degreeStore.courses['ignored'].length ? 4 : 3) : 12">
            <div
              id="drop-zone-ignored-courses"
              class="drop-zone"
              :class="isDroppable('ignored') ? 'drop-zone-on' : 'drop-zone-off'"
              @dragend="onDrag($event, 'end', 'ignored')"
              @dragenter="onDrag($event,'enter', 'ignored')"
              @dragleave="onDrag($event, 'leave', 'ignored')"
              @dragexit="onDrag($event,'exit', 'ignored')"
              @dragover="onDrag($event,'over', 'ignored')"
              @dragstart="onDrag($event,'start', 'ignored')"
              @drop="dropToUnassign($event, 'ignored')"
            >
              <h3 id="ignored-header" class="font-size-20 font-weight-bold pb-0 text-no-wrap" tabindex="-1">Other Coursework</h3>
              <UnassignedCourses :ignored="true" />
            </div>
          </v-col>
          <v-col :cols="$vuetify.display.mdAndUp ? (degreeStore.courses['ignored'].length ? 4 : 5) : 12">
            <div
              id="drop-zone-unassigned-courses"
              class="drop-zone"
              :class="isDroppable('unassigned') ? 'drop-zone-on' : 'drop-zone-off'"
              @dragend="onDrag($event, 'end', 'unassigned')"
              @dragenter="onDrag($event,'enter', 'unassigned')"
              @dragleave="onDrag($event, 'leave', 'unassigned')"
              @dragexit="onDrag($event,'exit', 'unassigned')"
              @dragover="onDrag($event,'over', 'unassigned')"
              @dragstart="onDrag($event,'start', 'unassigned')"
              @drop="dropToUnassign($event, 'unassigned')"
            >
              <h3 id="unassigned-header" class="font-size-20 font-weight-bold pb-0 text-no-wrap" tabindex="-1">Unassigned Courses</h3>
              <div v-if="currentUser.canEditDegreeProgress" class="pb-2">
                <DuplicateExistingCourse />
              </div>
              <UnassignedCourses />
            </div>
          </v-col>
        </v-row>
      </v-container>
      <div class="mt-3">
        <h3 class="sr-only">Categories</h3>
        <v-container fluid>
          <v-row>
            <v-col
              v-for="position in [1, 2, 3]"
              :id="`student-degree-check-column-${position}`"
              :key="position"
              class="degree-check-column"
            >
              <TemplateCategoryColumn :position="position" />
            </v-col>
          </v-row>
        </v-container>
      </div>
    </div>
    <div v-if="contextStore.config.isVueAppDebugMode">
      <DebugTemplate />
    </div>
  </div>
</template>

<script setup>
import DebugTemplate from '@/components/degree/DebugTemplate'
import DuplicateExistingCourse from '@/components/degree/student/DuplicateExistingCourse'
import StudentDegreeCheckHeader from '@/components/degree/student/StudentDegreeCheckHeader'
import StudentProfileHeader from '@/components/student/profile/StudentProfileHeader'
import TemplateCategoryColumn from '@/components/degree/TemplateCategoryColumn'
import UnassignedCourses from '@/components/degree/student/UnassignedCourses'
import UnitRequirements from '@/components/degree/UnitRequirements'
import {alertScreenReader, setPageTitle} from '@/lib/utils'
import {getStudentBySid} from '@/api/student'
import {onDrop, refreshDegreeTemplate} from '@/stores/degree-edit-session/utils'
import {computed, onMounted, onUnmounted, ref} from 'vue'
import {useContextStore} from '@/stores/context'
import {useDegreeStore} from '@/stores/degree-edit-session/index'
import {useRoute} from 'vue-router'
import {get} from 'lodash'

const contextStore = useContextStore()
const degreeStore = useDegreeStore()
const currentUser = contextStore.currentUser
const loading = computed(() => contextStore.loading)
const previousClientY = ref(0)
const scrollHeight = ref(undefined)
const student = ref(undefined)

contextStore.loadingStart()

onMounted(() => {
  onResize()
  window.addEventListener('resize', onResize)
  window.addEventListener('scroll', onResize)

  const degreeId = useRoute().params.id
  refreshDegreeTemplate(degreeId).then(() => {
    getStudentBySid(degreeStore.sid, true).then(data => {
      student.value = data
      contextStore.loadingComplete()
      const studentName = currentUser.inDemoMode ? 'Student' : student.value.name
      setPageTitle(`${studentName} - ${degreeStore.degreeName}`)
      alertScreenReader(`${degreeStore.degreeName} for ${student.value.name}`)
    })
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  window.removeEventListener('scroll', onResize)
})

const dropToUnassign = (event, context) => {
  event.stopPropagation()
  event.preventDefault()
  onDrop(null, context)
  degreeStore.setDraggingTarget(null)
}

const isDroppable = target => {
  const course = degreeStore.draggingContext.course
  let droppable = degreeStore.draggingContext.target === target && course
  if (droppable) {
    if (target === 'ignored') {
      droppable = !course.ignore
    } else {
      droppable = course.ignore || course.categoryId
    }
  }
  return droppable
}

const onDrag = (event, stage, context) => {
  switch (stage) {
  case 'end':
    degreeStore.setDraggingTarget(null)
    degreeStore.draggingContextReset()
    break
  case 'enter':
  case 'over':
    event.stopPropagation()
    event.preventDefault()
    degreeStore.setDraggingTarget(context)
    break
  case 'leave':
    if (get(event.target, 'id') === `drop-zone-${context}-courses`) {
      degreeStore.setDraggingTarget(null)
    }
    break
  case 'exit':
  case 'start':
  default:
    break
  }
}

const scrollTo = event => {
  // Firefox does not need the intervention below.
  if (degreeStore.draggingContext.course && navigator.userAgent.indexOf('Firefox') === -1) {
    const eventY = event.clientY
    // Distance to bottom of viewport
    const distanceToBottom = window.innerHeight - eventY
    const magicNumber = 100
    // The closer to viewport top, or bottom, the faster the scroll.
    if (eventY >= previousClientY.value && distanceToBottom < magicNumber) {
      window.scrollTo({behavior: 'smooth', top: scrollHeight.value + magicNumber - distanceToBottom})
    } else if (eventY <= previousClientY.value && eventY < magicNumber) {
      window.scrollTo({behavior: 'smooth', top: window.scrollY + eventY - magicNumber})
    }
    previousClientY.value = eventY
  }
}

const onResize = () => {
  scrollHeight.value = window.scrollY
}
</script>

<style scoped>
.column-spacer {
  max-width: 10px;
  min-width: 10px;
}
.cursor-grabbing {
  cursor: grabbing !important;
}
.degree-check-column {
  min-width: 300px;
  padding-bottom: 10px;
}
.drop-zone {
  margin-bottom: 0.5em;
  padding: 0.5em;
}
.drop-zone-on {
  background-color: #ecf5fb;
  border: #8bbdda dashed 0.15em;
}
.drop-zone-off {
  border: transparent dashed 0.15em;
}
.section-separator {
  border-bottom: 1px #999 solid;
}
.unit-requirements {
  margin-bottom: 0.5em;
  padding: 0.5em;
}
</style>
