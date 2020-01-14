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
        <h3 class="border-bottom page-section-header-sub pb-2 pt-3">Notes (BOA)</h3>
        <div class="d-flex justify-content-between">
          <div>
            <label for="notes-count-boa">Total</label>
          </div>
          <div id="notes-count-boa" class="font-weight-bolder">
            {{ report.boa.notes.count.total | numFormat }}
          </div>
        </div>
        <div class="d-flex justify-content-between">
          <div>
            <label for="notes-count-boa-authors">Distinct authors</label>
          </div>
          <div id="notes-count-boa-authors" class="font-weight-bolder">
            {{ report.boa.notes.count.authors.total | numFormat }}
          </div>
        </div>
      </div>

      <div class="pt-4">
        <h3 class="border-bottom page-section-header-sub pb-2 pt-3">{{ report.dept.name }} Notes (BOA)</h3>

        <div class="d-flex justify-content-between">
          <div>
            <label :for="`notes-count-boa-${report.dept.code}`">Total</label>
          </div>
          <div :id="`notes-count-boa-${report.dept.code}`" class="font-weight-bolder">
            {{ get(report.boa.notes.count, deptCode) | numFormat }}
          </div>
        </div>
        <div class="d-flex justify-content-between">
          <div>
            <label :for="`notes-count-boa-authors-${report.dept.code}`">Distinct authors</label>
          </div>
          <div :id="`notes-count-boa-authors-${report.dept.code}`" class="font-weight-bolder">
            {{ get(report.boa.notes.count.authors, deptCode) | numFormat }}
          </div>
        </div>
      </div>

      <div class="pt-4">
        <h3 class="border-bottom page-section-header-sub pb-2 pt-3">Notes (CalCentral)</h3>
        <div class="d-flex justify-content-between">
          <div>
            <label for="notes-count-calcentral">Total</label>
          </div>
          <div id="notes-count-calcentral" class="font-weight-bolder">
            {{ report.sis.notes.count | numFormat }}
          </div>
        </div>
      </div>

      <div class="pt-4">
        <h3 class="border-bottom page-section-header-sub pb-2 pt-3">Users</h3>
        <div>
          TODO: Number of users who have accessed BOA, and their departmental affiliations
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
