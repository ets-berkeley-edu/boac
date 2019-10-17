<template>
  <div class="p-3">
    <Spinner />
    <div v-if="!loading">
      <Users
        v-if="users"
        :users="users" />
    </div>
  </div>
</template>

<script>
import Loading from '@/mixins/Loading';
import Users from '@/components/admin/Users';
import Spinner from '@/components/util/Spinner';
import store from '@/store';

export default {
  name: 'PassengerManifest',
  components: {Spinner, Users},
  mixins: [Loading],
  data: () => ({
    active: [],
    users: null
  }),
  mounted() {
    store.dispatch('user/loadUsers').then(data => {
      this.users = data;
      this.loaded();
    });
  }
}
</script>
