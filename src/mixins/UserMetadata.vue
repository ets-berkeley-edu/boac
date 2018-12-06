<script>
import _ from 'lodash';
import store from '@/store';

export default {
  name: 'UserMetadata',
  data: () => ({
    inDemoMode: null,
    isAscUser: undefined,
    canViewAsc: undefined
  }),
  created() {
    this.inDemoMode = _.get(store.getters, 'user.inDemoMode');
    this.isAscUser = this.$_UserMetadata_isDepartmentMember('UWASC');
    this.canViewAsc =
      _.get(store.getters, 'user.isAdmin') &&
      this.$_UserMetadata_isDepartmentMember('UWASC');
  },
  computed: {
    user: () => store.getters.user
  },
  methods: {
    $_UserMetadata_isDepartmentMember: deptCode => {
      _.get(store.getters.user, `departments.${deptCode}.isAdvisor`) ||
        _.get(store.getters.user, `departments.${deptCode}.isDirector`);
    }
  }
};
</script>
