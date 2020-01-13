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
              <h1 class="page-section-header">Analytics</h1>
            </div>
          </div>
          <div v-if="availableDepartments.length === 1">
            <h2 class="page-section-header-sub pt-0">{{ report.dept.name }}</h2>
          </div>
          <div v-if="availableDepartments.length > 1" class="align-items-center d-flex">
            <label class="sr-only" for="available-department-reports">Departments:</label>
            <div>
              <b-form-select
                id="available-department-reports"
                v-model="deptCode"
                :options="availableDepartments"
                class="form-control p-1 pl-3 pr-2 w-auto"
                text-field="name"
                value-field="code"
                @change="renderReport">
              </b-form-select>
            </div>
          </div>
        </div>
      </div>
      <div class="pt-4">
        <h3 class="page-section-header-sub">Notes</h3>
        <div>
          Yo!
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import Loading from '@/mixins/Loading';
import Spinner from '@/components/util/Spinner';
import Util from '@/mixins/Util';
import { getAvailableDepartmentReports, getBoaUsageSummary } from '@/api/reports';

export default {
  name: 'Admin',
  components: {
    Spinner
  },
  mixins: [Context, Loading, Util],
  data: () => ({
    availableDepartments: undefined,
    deptCode: undefined,
    report: undefined
  }),
  mounted() {
    this.deptCode = this.trim(this.get(this.$route, 'params.deptCode')).toUpperCase();
    this.renderReport();
  },
  methods: {
    renderReport() {
      this.loadingStart();
      getAvailableDepartmentReports().then(departments => {
        if (this.includes(this.map(departments, 'code'), this.deptCode)) {
          this.availableDepartments = departments;
          getBoaUsageSummary(this.deptCode).then(report => {
            if (report) {
              this.report = report;
              this.loaded('Analytics');
            } else {
              this.$router.push({ path: '/404' });
            }
          });
        } else {
          this.$router.push({ path: '/404' });
        }
      });
    }
  }
};
</script>
