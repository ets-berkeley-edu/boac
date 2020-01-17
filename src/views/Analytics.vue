<template>
  <div class="p-3">
    <Spinner alert-prefix="Analytics page" />
    <div v-if="!loading">
      <div class="d-flex justify-content-between">
        <div>
          <div class="align-items-center d-flex pb-0">
            <div class="pr-3">
              <font-awesome :style="{ color: '#3b7ea5' }" icon="chart-line" size="2x" />
            </div>
            <div class="pt-2">
              <h1 class="page-section-header">Flight Data Recorder</h1>
            </div>
          </div>
          <div v-if="availableDepartments.length === 1">
            <h2 class="page-section-header-sub pt-0">{{ department.name }}</h2>
          </div>
          <div v-if="availableDepartments.length > 1" class="align-items-center d-flex">
            <label class="sr-only" for="available-department-reports">Departments:</label>
            <div>
              <b-form-select
                id="available-department-reports"
                v-model="deptCode"
                :options="availableDepartments"
                class="form-control pb-1 pl-3 pr-5 pt-1 w-auto"
                text-field="name"
                value-field="code"
                @change="render">
              </b-form-select>
            </div>
          </div>
        </div>
      </div>
      <NotesReport :department="department" />
      <UserReport :department="department" />
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import Loading from '@/mixins/Loading';
import NotesReport from "@/components/reports/NotesReport";
import Spinner from '@/components/util/Spinner';
import UserReport from "@/components/reports/UserReport";
import Util from '@/mixins/Util';
import { getAvailableDepartmentReports } from '@/api/reports';

export default {
  name: 'Admin',
  components: {
    NotesReport,
    Spinner,
    UserReport
  },
  mixins: [Context, Loading, Util],
  data: () => ({
    availableDepartments: undefined,
    department: undefined,
  }),
  mounted() {
    this.deptCode = this.trim(this.get(this.$route, 'params.deptCode')).toUpperCase();
    getAvailableDepartmentReports().then(departments => {
      this.availableDepartments = departments;
      this.render();
      this.loaded('Reports');
    });
  },
  methods: {
    render() {
      this.department = this.find(this.availableDepartments, ['code', this.deptCode]);
    }
  }
};
</script>
