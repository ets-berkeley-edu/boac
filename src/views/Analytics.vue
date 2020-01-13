<template>
  <div class="p-3">
    <Spinner alert-prefix="Analytics page" />
    <div v-if="!loading">
      <div class="align-items-center d-flex pb-0">
        <div class="pr-3">
          <font-awesome :style="{ color: '#3b7ea5' }" icon="chart-line" size="2x" />
        </div>
        <div class="pt-2">
          <h1 class="page-section-header">Analytics</h1>
        </div>
      </div>
      <div>
        <h2 class="page-section-header-sub pt-0">{{ report.dept.name }}</h2>
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
import { getBoaUsageSummary } from '@/api/reports';

export default {
  name: 'Admin',
  components: {
    Spinner
  },
  mixins: [Context, Loading, Util],
  data: () => ({
    department: undefined,
    report: undefined
  }),
  mounted() {
    const deptCode = this.trim(this.get(this.$route, 'params.deptCode')).toLowerCase();
    if (deptCode) {
      getBoaUsageSummary(deptCode).then(report => {
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
  }
};
</script>
