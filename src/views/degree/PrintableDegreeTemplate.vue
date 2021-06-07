<template>
  <div class="m-4">
    <Spinner />
    <div v-if="!loading">
      <b-container fluid>
        <b-row>
          <b-col v-if="student">
            <h1 class="font-size-14 font-weight-bold" :class="{'demo-mode-blur': $currentUser.inDemoMode}">{{ student.name }}</h1>
            <div class="font-weight-bold">
              SID <span :class="{'demo-mode-blur': $currentUser.inDemoMode}">{{ student.sid }}</span>
            </div>
            <div class="font-weight-bold">
              {{ student.sisProfile.level.description }}
            </div>
            <div class="text-secondary">{{ student.sisProfile.termsInAttendance }} Terms in Attendance</div>
            <div class="text-secondary">Expected graduation {{ student.sisProfile.expectedGraduationTerm.name }}</div>

            <div class="pt-2">
              <span class="font-weight-bold p-0 text-secondary">MAJOR</span>
              <hr class="subsection-divider my-1 mr-5" />
              <div
                v-for="plan in student.sisProfile.plans"
                :key="plan.description"
              >
                <div class="font-weight-bold">{{ plan.description }}</div>
                <div class="text-secondary">{{ plan.program }}</div>
              </div>
            </div>
            <div v-if="student.sisProfile.plansMinor.length" class="pt-2">
              <span class="font-weight-bold mt-2 p-0 text-secondary">MINOR</span>
              <hr class="subsection-divider my-1 mr-5" />
              <div v-for="minorPlan of student.sisProfile.plansMinor" :key="minorPlan.description">
                <div class="font-weight-bold">{{ minorPlan.description }}</div>
                <div class="text-secondary">{{ minorPlan.program }}</div>
              </div>
            </div>
          </b-col>
          <b-col id="degree-unit-requirements-info">
            <div class="unofficial-label-pill">UNOFFICIAL DEGREE PROGRESS REPORT </div>
            <h1 class="font-size-12 pt-2">{{ degreeName }}</h1>
            <h4 class="font-size-10 font-weight-bold mb-0">Unit Requirements</h4>
            <UnitRequirements />
          </b-col>
        </b-row>
      </b-container>
      <hr class="divider ml-3 mr-3" />
      <b-container fluid>
        <b-row>
          <b-col
            v-for="position in [1, 2, 3]"
            :key="position"
            class="print-degree-progress-column"
          >
            <template>
              <div>
                <div
                  v-for="category in $_.filter(categories, c => c.position === position && $_.isNil(c.parentCategoryId))"
                  :key="category.id"
                  class="print-degree-course-requirements"
                >
                  <Category
                    v-if="category.id"
                    :category="category"
                    :position="position"
                    :printable="true"
                  />
                  <div v-if="$_.size(category.courseRequirements)" class="pl-1 py-2">
                    <CoursesTable
                      :items="category.courseRequirements"
                      :parent-category="category"
                      :position="position"
                      :printable="true"
                    />
                  </div>
                  <div v-if="$_.size(category.subcategories)">
                    <div v-for="subcategory in category.subcategories" :key="subcategory.id">
                      <Category
                        v-if="subcategory.id"
                        :category="subcategory"
                        :position="position"
                        :printable="true"
                      />
                      <div v-if="$_.size(subcategory.courseRequirements)" class="pl-1 py-2">
                        <CoursesTable
                          :items="subcategory.courseRequirements"
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
      </b-container>

      <div v-if="degreeNote && includeNotesWhenPrint" class="ml-3">
        <hr class="divider" />
        <h1 id="degree-note" class="font-size-10 font-weight-bold">Degree Notes</h1>
        <div class="font-size-8">
          {{ degreeNote.body }}
        </div>
      </div>
    </div>
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
    student: undefined
  }),
  created() {
    const id = this.toInt(this.$_.get(this.$route, 'params.id'))
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
.divider {
  background-color: #999;
  border: none;
  color: #999;
  height: 3px;
}
.font-size-10 {
  font-size: 10px;
}
.font-size-8 {
  font-size: 8px;
}
.subsection-divider {
  background-color: #999999;
  height: 1px;
}
.unofficial-label-pill {
  background-color: #000000;
  border: 1px solid #000000;
  border-radius: 5px;
  color: #fff;
  font-size: 8px;
  font-weight: bold;
  height: 24px;
  margin-top: 2px;
  padding-top: 6px;
  text-align: center;
  width: auto;
}
</style>
