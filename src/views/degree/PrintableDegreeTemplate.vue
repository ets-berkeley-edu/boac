<template>
  <div class="m-4">
    <Spinner />
    <div v-if="!loading">
      <!-- TO DO: Create IDs for necessary elements -->
      <b-container class="pr-3" fluid>
        <b-row>
          <b-col v-if="student" id="student-degree-info" class="font-size-12">
            <h1 class="font-size-14 font-weight-bold"> {{ student.name }} </h1>

            <div class="font-weight-bold">SID {{ student.sid }}</div>
            <div class="font-weight-bold">{{ student.sisProfile.level.description }}</div>
            <div class="text-secondary">{{ student.sisProfile.termsInAttendance }} Terms in Attendance</div>
            <div class="text-secondary">Expected graduation {{ student.sisProfile.expectedGraduationTerm.name }}</div>

            <div class="pt-2">
              <span class="font-weight-bold p-0 text-secondary">MAJOR</span>
              <hr class="subsection-divider my-1 mr-5" />
              <!-- TO DO: Add support for undeclared students (intendedMajor) -->
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
              <div
                v-for="minorPlan of student.sisProfile.plansMinor"
                :key="minorPlan.description"
              >
                <div class="font-weight-bold">{{ minorPlan.description }}</div>
                <div class="text-secondary">{{ minorPlan.program }}</div>
              </div>
            </div>
          </b-col>
          <b-col id="degree-unit-requirements-info">
            <div class="unofficial-label-pill">UNOFFICIAL DEGREE PROGRESS REPORT </div>
            <h1 class="font-size-14 pt-2">{{ template.name }}</h1>

            <h4 class="font-size-12 mb-0">Unit Requirements</h4>
            <div v-if="$_.isEmpty(template.unitRequirements)" class="no-data-text">
              No unit requirements created
            </div>
            <b-table
              id="print-unit-requirements-table"
              :items="template.unitRequirements"
              :fields="fields"
              thead-class="sortable-table-header text-nowrap border-bottom"
              borderless
              responsive
              small
            >
            </b-table>
            <hr class="subsection-divider mb-0" />
            <div class="font-weight-bold pt-1">
              <!-- TO DO: Figure out how to position this correctly -->
              <span class="float-left">
                Total Units:
              </span>
              <span class="pl-4">
                {{ totalUnits }}
              </span>
            </div>
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
                  v-for="category in $_.filter(template.categories, c => c.position === position && $_.isNil(c.parentCategoryId))"
                  :key="category.id"
                  class="print-degree-course-requirements"
                >
                  <Category
                    v-if="category.id"
                    :category="category"
                    :position="position"
                  />
                  <div v-if="$_.size(category.courseRequirements)" class="pl-1 py-2">
                    <CoursesTable
                      :category="category"
                      :items="category.courseRequirements"
                      :position="position"
                    />
                  </div>
                  <div v-if="$_.size(category.subcategories)">
                    <div v-for="subcategory in category.subcategories" :key="subcategory.id">
                      <Category
                        v-if="subcategory.id"
                        :category="subcategory"
                        :position="position"
                      />
                      <div v-if="$_.size(subcategory.courseRequirements)" class="pl-1 py-2">
                        <CoursesTable
                          :category="subcategory"
                          :items="subcategory.courseRequirements"
                          :position="position"
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
    </div>
  </div>
</template>


<script>
import Category from '@/components/degree/Category.vue'
import Context from '@/mixins/Context'
import CoursesTable from '@/components/degree/CoursesTable.vue'
import Loading from '@/mixins/Loading'
import Spinner from '@/components/util/Spinner'
import Util from '@/mixins/Util'
import {getDegreeTemplate} from '@/api/degree'
import {getStudentBySid} from '@/api/student'

export default {
  name: 'PrintableDegreeTemplate',
  components: {
    Spinner,
    CoursesTable,
    Category
  },
  mixins: [Context, Loading, Util],
  mounted() {
    const id = this.toInt(this.$_.get(this.$route, 'params.id'))

    getDegreeTemplate(id).then(data => {
      this.template = data
      if (data.sid) {
        getStudentBySid(data.sid).then(studentData => {
          this.student = studentData
          this.loaded(`Print ${this.template.name} degree check for ${this.student.name} has loaded`)
        })
      } else {
        this.loaded(`Print ${this.template.name} degree check has loaded`)
      }
    })
  },
  data: () => ({
    fields: [
      {
        key: 'name',
        label: 'Type',
        class: 'pl-0'
      },
      {
        key: 'minUnits',
        label: 'Min.',
        class: 'text-right'
      },
      {
        key: 'completedUnits',
        label: 'Completed'
      }
    ],
    template: undefined,
    student: undefined
  }),
  computed: {
    totalUnits() {
      // TO DO: gather completed units and subtract to get actual total units
      return this.$_.map(this.template.unitRequirements, 'minUnits')
        .reduce((accumulator, val) => accumulator + val)
    }
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
.print-degree-courses > div > table > tbody > tr > td {
  font-size: 10px;
  padding: 1px;
}
.print-degree-courses > div > table > thead > tr > th {
  font-size: 8px;
}
.print-degree-course-requirements >>> button {
  display: none;
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
  font-family: Helvetica;
  font-size: 8px;
  font-weight: bold;
  height: 24px;
  margin-top: 2px;
  padding-top: 6px;
  text-align: center;
  width: auto;
}
#degree-progress-category-description {
  font-size: 10px;
}
#print-unit-requirements-table > tbody > tr > td {
  padding: .1rem;
}
#print-unit-requirements-table > thead {
  font-size: 8px;
}
#print-unit-requirements-table {
  font-size: 8px;
}
</style>
