<script>
import store from '@/store';

export default {
  name: 'StudentMetadata',
  methods: {
    displayAsInactive(student) {
      const user = store.getters.user;
      return (
        (user && (user.isAsc && !student.athleticsProfile.isActiveAsc)) ||
        (user.isCoe && !student.coeProfile.isActiveCoe)
      );
    },
    setSortableName: student =>
      (student.sortableName = student.lastName + ', ' + student.firstName)
  }
};
</script>
