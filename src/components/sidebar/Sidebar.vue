<template>
  <div>
    <div>
      <SearchForm
        :domain="domain"
        context="sidebar" />
    </div>
    <div v-if="myCohorts">
      <Cohorts />
      <hr class="ml-2 mr-2 section-divider" />
    </div>
    <div v-if="myCuratedGroups">
      <CuratedGroups />
      <hr class="ml-2 mr-2 section-divider" />
    </div>
    <div v-if="$config.featureFlagAdmittedStudents && myAdmitCohorts">
      <MyAdmitCohorts />
      <hr class="ml-2 mr-2 section-divider" />
    </div>
    <div class="mb-2 sidebar-row-link">
      <div class="ml-2 mr-2">
        <router-link id="cohorts-all" to="/cohorts/all">Everyone's Cohorts</router-link>
      </div>
    </div>
    <div class="mb-2 sidebar-row-link">
      <div class="ml-2 mr-2">
        <router-link id="groups-all" to="/groups/all">Everyone's Groups</router-link>
      </div>
    </div>
    <div v-if="!$currentUser.isAdmin && $currentUser.canAccessAdvisingData">
      <div class="batch-note-button fixed-bottom mb-3">
        <CreateNoteModal id="batch-note-button" />
      </div>
    </div>
  </div>
</template>

<script>
import Cohorts from '@/components/sidebar/Cohorts.vue';
import Context from '@/mixins/Context';
import CreateNoteModal from '@/components/note/create/CreateNoteModal.vue';
import CuratedGroups from '@/components/sidebar/CuratedGroups.vue';
import CurrentUserExtras from '@/mixins/CurrentUserExtras';
import MyAdmitCohorts from '@/components/sidebar/MyAdmitCohorts.vue';
import Util from '@/mixins/Util.vue';
import SearchForm from '@/components/sidebar/SearchForm.vue';

export default {
  name: 'Sidebar',
  components: {
    Cohorts,
    CreateNoteModal,
    CuratedGroups,
    MyAdmitCohorts,
    SearchForm
  },
  mixins: [Context, CurrentUserExtras, Util],
  computed: {
    domain() {
      let domain = ['students'];
      if (this.$currentUser.canAccessCanvasData) {
        domain.push('courses');
      }
      if (this.$currentUser.canAccessAdvisingData) {
        domain.push('notes');
      }
      if (this.includeAdmits) {
        domain.push('admits');
      }
      return domain;
    }
  }
};
</script>

<style>
.batch-note-button {
  width: 17%;
}
.section-divider {
  background-color: #4a90e2;
  border: none;
  color: #4a90e2;
  height: 1px;
}
.sidebar-header {
  color: #fff;
  font-size: 16px;
  font-weight: 800;
}
.sidebar-pill {
  background-color: #8bbdda;
  border-radius: 10px;
  color: #125704;
  display: inline-block;
  float: right;
  font-size: 16px;
  font-weight: 800;
  height: 20px;
  line-height: 20px;
  padding: 0 4px 0 4px;
  text-align: center;
}
.sidebar-row-link {
  border-left: 6px solid #125074;
  color: #8bbdda;
  font-size: 16px;
}
.sidebar-row-link:hover,
.sidebar-row-link:focus,
.sidebar-row-link:active {
  border-left: 6px solid #f0ad4e !important;
  background-color: #083456;
  border: 0;
  color: #f0ad4e;
  text-decoration: none;
  -moz-outline-style: none;
}
.sidebar-row-link:hover .sidebar-pill,
.sidebar-row-link:focus .sidebar-pill,
.sidebar-row-link:active .sidebar-pill {
  background-color: #f0ad4e;
  color: #083456;
}
.sidebar-row-link a:link,
.sidebar-row-link a:visited {
  text-decoration: none;
  border: 0;
  color: inherit;
  -moz-outline-style: none;
}
</style>
