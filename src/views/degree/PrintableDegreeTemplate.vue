<template>
  <v-container v-if="!loading" fluid>
    <v-row class="pb-2">
      <v-col v-if="student">
        <h1 class="font-size-18 font-weight-bold mb-0" :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ student.name }}</h1>
        <div class="font-size-14">
          <div class="font-weight-500">
            SID <span :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ student.sid }}</span>
            <div>
              {{ get(student, 'sisProfile.level.description') || 'Level not available' }}
            </div>
            <div>
              <div v-if="get(student, 'sisProfile.termsInAttendance')">
                {{ student.sisProfile.termsInAttendance }} Terms in Attendance
              </div>
              <div v-if="!get(student, 'sisProfile.termsInAttendance')">
                Terms in Attendance not available
              </div>
              <div>Expected graduation {{ get(student, 'sisProfile.expectedGraduationTerm.name') || 'not available' }}</div>
            </div>
          </div>
          <div v-if="student.sisProfile.plans.length" class="pt-2">
            <div class="section-border-minor">
              <span class="font-weight-bold pa-0 text-uppercase">Major</span>
            </div>
            <div v-for="(plan, index) in student.sisProfile.plans" :key="index">
              <div class="font-weight-bold">{{ plan.description }}</div>
              <div>{{ plan.program }}</div>
            </div>
          </div>
          <div v-if="student.sisProfile.plansMinor.length" class="py-2">
            <div class="section-border-minor">
              <span class="font-weight-bold mt-2 pa-0 text-uppercase">Minor</span>
            </div>
            <div v-for="minorPlan of student.sisProfile.plansMinor" :key="minorPlan.description">
              <div class="font-weight-bold">{{ minorPlan.description }}</div>
              <div>{{ minorPlan.program }}</div>
            </div>
          </div>
        </div>
      </v-col>
      <v-col>
        <div class="unofficial-label-pill">
          <div>UNOFFICIAL DEGREE PROGRESS REPORT</div>
          <div>Printed by {{ currentUser.name }} on {{ DateTime.now().toFormat('MMM d, yyyy') }}</div>
        </div>
        <h2 class="font-size-14">{{ degreeStore.degreeName }}</h2>
        <div :class="{'unit-requirements-of-template': !student}">
          <UnitRequirements :printable="true" />
        </div>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col class="pr-0">
        <div class="section-border-major" />
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col
        v-for="position in [1, 2, 3]"
        :key="position"
        :class="{'pr-2': position > 1}"
      >
        <div
          v-for="category in _filter(degreeStore.categories, c => c.position === position && isNil(c.parentCategoryId))"
          :key="category.id"
          class="mt-4"
          :class="{'pr-3': position < 3}"
        >
          <Category
            v-if="category.id"
            :category="category"
            :position="position"
            :printable="true"
          />
          <div v-if="!category.subcategories.length" class="py-1">
            <CoursesTable
              :id="`column-${position}-category-${category.id}-courses`"
              :items="getItemsForCoursesTable(category)"
              :parent-category="category"
              :position="position"
              :printable="true"
            />
          </div>
          <div v-if="size(category.subcategories)">
            <div v-for="subcategory in category.subcategories" :key="subcategory.id" class="pt-2">
              <Category
                v-if="subcategory.id"
                :category="subcategory"
                :position="position"
                :printable="true"
              />
              <div class="py-1">
                <CoursesTable
                  :items="getItemsForCoursesTable(subcategory)"
                  :parent-category="subcategory"
                  :position="position"
                  :printable="true"
                />
              </div>
            </div>
          </div>
        </div>
      </v-col>
    </v-row>
    <v-row v-if="degreeStore.degreeNote && includeNote">
      <v-col class="pb-5 pt-3">
        <h3 id="degree-note" class="font-size-12 font-weight-bold">Degree Notes</h3>
        <pre class="border-0 text-wrap" v-html="degreeStore.degreeNote.body" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import Category from '@/components/degree/Category.vue'
import CoursesTable from '@/components/degree/CoursesTable.vue'
import UnitRequirements from '@/components/degree/UnitRequirements'
import {alertScreenReader, setPageTitle, toBoolean, toInt} from '@/lib/utils'
import {computed, onMounted, ref} from 'vue'
import {filter as _filter, get, isNil, size} from 'lodash'
import {getItemsForCoursesTable} from '@/lib/degree-progress'
import {getStudentBySid} from '@/api/student'
import {refreshDegreeTemplate} from '@/stores/degree-edit-session/utils'
import {useContextStore} from '@/stores/context'
import {useDegreeStore} from '@/stores/degree-edit-session/index'
import {useRoute} from 'vue-router'
import {DateTime} from 'luxon'

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const degreeStore = useDegreeStore()
const includeNote = ref(undefined)
const loading = computed(() => contextStore.loading)
const student = ref(undefined)

contextStore.loadingStart()

onMounted(() => {
  const route = useRoute()
  const id = toInt(route.params.id)
  includeNote.value = toBoolean(route.query.includeNote)
  refreshDegreeTemplate(id).then(() => {
    if (degreeStore.sid) {
      getStudentBySid(degreeStore.sid).then(data => {
        student.value = data
        const studentName = currentUser.inDemoMode ? 'Student' : student.value.name
        setPageTitle(`${studentName} - ${degreeStore.degreeName}`)
        contextStore.loadingComplete()
        alertScreenReader(`${degreeStore.degreeName} for ${student.value.name}`)
      })
    } else {
      setPageTitle(degreeStore.degreeName)
      contextStore.loadingComplete()
      alertScreenReader(`${degreeStore.degreeName} is ready to print.`)
    }
  })
})
</script>

<style scoped>
@media print{
  @page {
    size: landscape;
  }
}
pre {
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  font-size: 12px;
  margin: 0;
}
.section-border-major {
  border-bottom: 3px #999 solid;
}
.section-border-minor {
  border-bottom: 1px #999 solid;
}
.unit-requirements-of-template {
  width: 34%;
}
.unofficial-label-pill {
  background-color: #000000;
  border-radius: 5px;
  color: #fff;
  print-color-adjust: exact;
  font-size: 12px;
  font-weight: bold;
  margin-bottom: 12px;
  padding: 6px 0 6px 0;
  text-align: center;
  width: auto;
}
</style>
