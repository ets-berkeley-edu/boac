<template>
  <div class="p-3">
    <Spinner />
    <div v-if="!loading">
      <div class="d-flex justify-content-between">
        <div>
          <div class="align-items-center d-flex pb-0">
            <div class="pr-2">
              <font-awesome :style="{color: '#3b7ea5'}" icon="chart-pie" size="2x" />
            </div>
            <div class="pt-2">
              <h1 class="page-section-header">Flight Data Recorder</h1>
            </div>
          </div>
        </div>
      </div>
      <NotesReport :department="department" />
      <div class="pb-4 pt-4">
        <h2 class="page-section-header-sub m-0 pt-0" :class="{'sr-only': availableDepartments.length !== 1}">{{ department.name }}</h2>
        <div v-if="availableDepartments.length > 1" class="align-items-center d-flex">
          <label class="sr-only" for="available-department-reports">Departments:</label>
          <div>
            <select
              id="available-department-reports"
              v-model="deptCode"
              class="form-control font-size-16 pb-1 pl-2 pr-5 pt-1 w-auto"
              style="font-size: 16px;"
              @change="render"
            >
              <option
                v-for="department in availableDepartments"
                :key="department.code"
                :value="department.code"
              >
                {{ department.name }}
              </option>
            </select>
          </div>
        </div>
      </div>
      <UserReport :department="department" />
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import NotesReport from '@/components/reports/NotesReport'
import Spinner from '@/components/util/Spinner'
import UserReport from '@/components/reports/UserReport'
import Util from '@/mixins/Util'
import {getAvailableDepartmentReports} from '@/api/reports'

export default {
  name: 'FlightDataRecorder',
  components: {
    NotesReport,
    Spinner,
    UserReport
  },
  mixins: [Context, Util],
  data: () => ({
    availableDepartments: undefined,
    department: undefined,
  }),
  mounted() {
    this.deptCode = this._trim(this._get(this.$route, 'params.deptCode')).toUpperCase()
    getAvailableDepartmentReports().then(departments => {
      if (this._includes(this._map(departments, 'code'), this.deptCode)) {
        this.availableDepartments = departments
        this.render()
        this.loadingComplete('Reports loaded')
      } else {
        this.$router.push({path: '/404'})
      }
    })
  },
  methods: {
    render() {
      this.department = this._find(this.availableDepartments, ['code', this.deptCode])
    }
  }
}
</script>
