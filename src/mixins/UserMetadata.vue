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
    this.inDemoMode = _.get(this.user, 'inDemoMode');
    this.isAscUser = this.$_UserMetadata_isDepartmentMember('UWASC');
    this.canViewAsc =
      _.get(this.user, 'isAdmin') &&
      this.$_UserMetadata_isDepartmentMember('UWASC');
  },
  computed: {
    myCohorts: () => store.getters['cohort/myCohorts'],
    myCuratedGroups: () => store.getters['curated/myCuratedGroups'],
    user: () => store.getters['user/currentUser']
  },
  methods: {
    $_UserMetadata_isDepartmentMember: deptCode => {
      let user = store.getters['user/currentUser'];
      return (
        _.get(user, `departments.${deptCode}.isAdvisor`) ||
        _.get(user, `departments.${deptCode}.isDirector`)
      );
    }
  }
};
</script>
