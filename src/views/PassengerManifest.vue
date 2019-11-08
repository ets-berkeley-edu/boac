<template>
  <div class="p-3">
    <Spinner alert-prefix="The Passenger Manifest" />
    <div v-if="!loading">
      <div class="list-group">
        <div class="align-items-center d-flex pb-1">
          <div class="pr-2">
            <font-awesome :style="{ color: '#3b7ea5' }" icon="clipboard-check" size="2x" />
          </div>
          <div class="pt-3">
            <h1 id="dept-users-section" class="page-section-header">
              Passengers
              <span class="font-size-14 text-black-50">(<a id="download-boa-users-csv" :href="`${apiBaseUrl}/api/users/csv`">download</a>)</span>
            </h1>
          </div>
        </div>
        <Users :departments="departments" />
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import Util from '@/mixins/Util';
import Loading from '@/mixins/Loading';
import Spinner from '@/components/util/Spinner';
import Users from '@/components/admin/Users';
import { getDepartments } from '@/api/user';

export default {
  name: 'PassengerManifest',
  components: {Spinner, Users},
  mixins: [Context, Loading, Util],
  data: () => ({
    departments: undefined
  }),
  created() {
    getDepartments(true).then(departments => {
      this.departments = departments;
      this.loaded('Passenger Manifest');
    });
  }
}
</script>
