<script>
import _ from 'lodash';
import store from '@/store';
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'UserMetadata',
  computed: {
    ...mapGetters('user', [
      'canViewAsc',
      'canViewCoe',
      'isAscUser',
      'isCoeUser',
      'preferences',
      'user',
      'userAuthStatus'
    ]),
    ...mapGetters('cohort', ['myCohorts']),
    ...mapGetters('curated', ['myCuratedGroups'])
  },
  methods: {
    ...mapActions('user', [
      'setUserPreference',
      'loadCalnetUserByCsid'
    ]),
    loadUserById(id) {
      return new Promise(resolve => {
        store.dispatch('user/loadUserGroups').then(userGroups => {
          const users = _.flatten(_.map(userGroups, 'users'));
          _.each(users, user => {
            if (user.id === id) {
              resolve(user);
              return false;
            }
          });
        });
      });
    }
  }
};
</script>
