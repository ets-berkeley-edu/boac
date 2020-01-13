<template>
  <div class="p-3">
    <Spinner alert-prefix="Analytics page" />
    <div v-if="!loading">
      <div class="align-items-center d-flex pb-3">
        <div class="pr-3">
          <font-awesome :style="{ color: '#3b7ea5' }" icon="chart-line" size="2x" />
        </div>
        <div class="pt-2">
          <h1 class="page-section-header">Analytics</h1>
        </div>
      </div>
      <div class="pt-2">
        <h2 class="page-section-header-sub">Notes</h2>
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

export default {
  name: 'Admin',
  components: {
    Spinner
  },
  mixins: [Context, Loading, Util],
  mounted() {
    this.loaded('Analytics');
  }
};
</script>
