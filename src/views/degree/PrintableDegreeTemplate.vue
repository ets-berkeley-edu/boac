<template>
  <div class="m-4">
    <Spinner />
    <b-container v-if="!loading" fluid>
      <b-row class="pb-2">
        <b-col v-if="student">
          <h1 class="font-size-18 font-weight-bold mb-0" :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ student.name }}</h1>
          <div class="font-size-14">
            <div class="font-weight-500">
              SID <span :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ student.sid }}</span>
              <div>
                {{ _get(student, 'sisProfile.level.description') || 'Level not available' }}
              </div>
              <div>
                <div v-if="_get(student, 'sisProfile.termsInAttendance')">
                  {{ student.sisProfile.termsInAttendance }} Terms in Attendance
                </div>
                <div v-if="!_get(student, 'sisProfile.termsInAttendance')">
                  Terms in Attendance not available
                </div>
                <div>Expected graduation {{ _get(student, 'sisProfile.expectedGraduationTerm.name') || 'not available' }}</div>
              </div>
            </div>
            <div v-if="student.sisProfile.plans.length" class="pt-2">
              <div class="section-border-minor">
                <span class="font-weight-bold p-0 text-uppercase">Major</span>
              </div>
              <div v-for="(plan, index) in student.sisProfile.plans" :key="index">
                <div class="font-weight-bold">{{ plan.description }}</div>
                <div>{{ plan.program }}</div>
              </div>
            </div>
            <div v-if="student.sisProfile.plansMinor.length" class="py-2">
              <div class="section-border-minor">
                <span class="font-weight-bold mt-2 p-0 text-uppercase">Minor</span>
              </div>
              <div v-for="minorPlan of student.sisProfile.plansMinor" :key="minorPlan.description">
                <div class="font-weight-bold">{{ minorPlan.description }}</div>
                <div>{{ minorPlan.program }}</div>
              </div>
            </div>
          </div>
        </b-col>
        <b-col>
          <div class="unofficial-label-pill">
            <div>UNOFFICIAL DEGREE PROGRESS REPORT</div>
            <div>Printed by {{ currentUser.name }} on {{ moment().format('MMMM D, YYYY') }}</div>
          </div>
          <h2 class="font-size-14">{{ degreeName }}</h2>
          <div :class="{'unit-requirements-of-template': !student}">
            <UnitRequirements :printable="true" />
          </div>
        </b-col>
      </b-row>
      <b-row>
        <b-col class="pr-0">
          <div class="mb-3 section-border-major" />
        </b-col>
      </b-row>
      <b-row>
        <b-col
          v-for="position in [1, 2, 3]"
          :key="position"
          :class="{'pr-2': position > 1}"
        >
          <div
            v-for="category in _filter(categories, c => c.position === position && _isNil(c.parentCategoryId))"
            :key="category.id"
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
            <div v-if="_size(category.subcategories)">
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
        </b-col>
      </b-row>
      <b-row v-if="degreeNote && includeNote">
        <b-col class="pb-5 pt-3">
          <h3 id="degree-note" class="font-size-12 font-weight-bold">Degree Notes</h3>
          <pre class="border-0 text-wrap" v-html="degreeNote.body" />
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
import Category from '@/components/degree/Category.vue'
import Context from '@/mixins/Context'
import CoursesTable from '@/components/degree/CoursesTable.vue'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import Spinner from '@/components/util/Spinner'
import UnitRequirements from '@/components/degree/UnitRequirements'
import Util from '@/mixins/Util'
import {getItemsForCoursesTable} from '@/lib/degree-progress'
import {getStudentBySid} from '@/api/student'
import {refreshDegreeTemplate} from '@/store/modules/degree-edit-session/utils'

export default {
  name: 'PrintableDegreeTemplate',
  components: {
    Category,
    CoursesTable,
    Spinner,
    UnitRequirements
  },
  mixins: [Context, DegreeEditSession, Util],
  data: () => ({
    includeNote: undefined,
    student: undefined
  }),
  created() {
    const id = this.toInt(this._get(this.$route, 'params.id'))
    this.includeNote = this.toBoolean(this.$route.query.includeNote)
    refreshDegreeTemplate(id).then(() => {
      if (this.sid) {
        getStudentBySid(this.sid).then(data => {
          this.student = data
          const studentName = this.currentUser.inDemoMode ? 'Student' : this.student.name
          this.setPageTitle(`${studentName} - ${this.degreeName}`)
          this.loadingComplete()
          this.alertScreenReader(`${this.degreeName} for ${this.student.name}`)
        })
      } else {
        this.setPageTitle(this.degreeName)
        this.loadingComplete()
        this.alertScreenReader(`${this.degreeName} is ready to print.`)
      }
    })
  },
  methods: {
    getItemsForCoursesTable
  }
}
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
  color-adjust: exact;
  font-size: 12px;
  font-weight: bold;
  margin-bottom: 12px;
  padding: 6px 0 6px 0;
  text-align: center;
  width: auto;
}
</style>
