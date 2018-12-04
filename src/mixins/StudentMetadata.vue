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
    }
  }
};
</script>
