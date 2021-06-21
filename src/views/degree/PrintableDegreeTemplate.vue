<template>
  <div class="m-4">
    <Spinner />
    <b-container v-if="!loading" fluid>
      <b-row>
        <b-col v-if="student" class="pr-5">
          <h1 class="font-size-14 font-weight-bold" :class="{'demo-mode-blur': $currentUser.inDemoMode}">{{ student.name }}</h1>
          <div class="font-size-12">
            <div class="font-weight-bold">
              SID <span :class="{'demo-mode-blur': $currentUser.inDemoMode}">{{ student.sid }}</span>
              <div>
                {{ student.sisProfile.level.description }}
              </div>
              <div class="text-secondary">
                {{ student.sisProfile.termsInAttendance }} Terms in Attendance
                <div>Expected graduation {{ student.sisProfile.expectedGraduationTerm.name }}</div>
              </div>
            </div>
            <div class="pt-2">
              <div class="py-2 section-border-minor">
                <span class="font-weight-bold p-0 text-secondary text-uppercase">Major</span>
              </div>
              <div
                v-for="(plan, index) in student.sisProfile.plans"
                :key="plan.description"
                :class="{'pt-2': index === 0}"
              >
                <div class="font-weight-bold">{{ plan.description }}</div>
                <div class="text-secondary">{{ plan.program }}</div>
              </div>
            </div>
            <div v-if="student.sisProfile.plansMinor.length" class="pt-2">
              <div class="section-border-minor">
                <span class="font-weight-bold mt-2 p-0 text-secondary text-uppercase">Minor</span>
              </div>
              <div v-for="minorPlan of student.sisProfile.plansMinor" :key="minorPlan.description">
                <div class="font-weight-bold">{{ minorPlan.description }}</div>
                <div class="text-secondary">{{ minorPlan.program }}</div>
              </div>
            </div>
          </div>
        </b-col>
        <b-col class="pr-0">
          <div class="unofficial-label-pill">
            <div>UNOFFICIAL DEGREE PROGRESS REPORT</div>
            <div>Printed by {{ $currentUser.name }} on {{ new Date() | moment('MMMM D, YYYY') }}</div>
          </div>
          <h2 class="font-size-14">{{ degreeName }}</h2>
          <UnitRequirements :printable="true" />
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
          class="print-degree-progress-column"
        >
          <template>
            <div>
              <div
                v-for="(category, index) in $_.filter(categories, c => c.position === position && $_.isNil(c.parentCategoryId))"
                :key="category.id"
                :class="{'pt-3': index > 0}"
              >
                <Category
                  v-if="category.id"
                  :category="category"
                  :position="position"
                  :printable="true"
                />
                <div v-if="!category.subcategories.length" class="pl-1 py-1">
                  <CoursesTable
                    :id="`column-${position}-category-${category.id}-courses`"
                    :items="getCourses(category)"
                    :parent-category="category"
                    :position="position"
                    :printable="true"
                  />
                </div>
                <div v-if="$_.size(category.subcategories)">
                  <div v-for="subcategory in category.subcategories" :key="subcategory.id" class="pl-2 pt-2">
                    <Category
                      v-if="subcategory.id"
                      :category="subcategory"
                      :position="position"
                      :printable="true"
                    />
                    <div class="pl-1 py-1">
                      <CoursesTable
                        :items="getCourses(subcategory)"
                        :parent-category="subcategory"
                        :position="position"
                        :printable="true"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </b-col>
      </b-row>
      <b-row v-if="degreeNote && includeNote">
        <b-col>
          <div class="mb-3 mt-2">
            <div class="footer-border pt-3">
              <h3 id="degree-note" class="font-size-12 font-weight-bold">Degree Notes</h3>
              <div class="font-size-12">
                {{ degreeNote.body }}
              </div>
            </div>
          </div>
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
import Loading from '@/mixins/Loading'
import Spinner from '@/components/util/Spinner'
import UnitRequirements from '@/components/degree/UnitRequirements'
import Util from '@/mixins/Util'
import {getStudentBySid} from '@/api/student'

export default {
  name: 'PrintableDegreeTemplate',
  components: {
    Category,
    CoursesTable,
    Spinner,
    UnitRequirements
  },
  mixins: [Context, DegreeEditSession, Loading, Util],
  data: () => ({
    includeNote: undefined,
    student: undefined
  }),
  created() {
    const id = this.toInt(this.$_.get(this.$route, 'params.id'))
    this.includeNote = this.toBoolean(this.$route.query.includeNote)
    this.init(id).then(() => {
      getStudentBySid(this.sid).then(data => {
        this.student = data
        const studentName = this.$currentUser.inDemoMode ? 'Student' : this.student.name
        this.setPageTitle(`${studentName} - ${this.degreeName}`)
        this.loaded(`${this.degreeName} for ${this.student.name}`)
      })
    })
  }
}
</script>

<style scoped>
.footer-border {
  border-top: 1px #999 solid;
}
.section-border-major {
  border-bottom: 3px #999 solid;
}
.section-border-minor {
  border-bottom: 1px #999 solid;
}
.unofficial-label-pill {
  background-color: #000000;
  border-radius: 5px;
  color: #fff;
  font-size: 12px;
  font-weight: bold;
  margin-bottom: 12px;
  padding: 6px 0 6px 0;
  text-align: center;
  width: auto;
}
</style>
