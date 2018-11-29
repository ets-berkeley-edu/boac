<template>
  <div v-if="user">
    <SearchStudents/>
    <Cohorts/>
    <hr class="section-divider"/>
    <CuratedGroups/>

    <div class="sidebar-row-link">
      <span class="sidebar-row-link-label">
        <router-link id="sidebar-filtered-cohorts-all"
                     to="/cohorts_all">Everyone's Cohorts</router-link>
      </span>
    </div>
  </div>
</template>

<script>
import store from '@/store';
import Cohorts from '@/components/sidebar/Cohorts.vue';
import CuratedGroups from '@/components/sidebar/CuratedGroups.vue';
import SearchStudents from '@/components/sidebar/SearchStudents.vue';

export default {
  name: 'Sidebar',
  components: {
    Cohorts,
    CuratedGroups,
    SearchStudents
  },
  computed: {
    user() {
      return store.getters.user;
    }
  }
};
</script>

<style>
.sidebar-header {
  color: #fff;
  font-size: 16px;
  font-weight: 800;
  margin: 1px 0 1px 0;
  white-space: nowrap;
}
.sidebar-row-link {
  border-left: 6px solid #125074;
  color: #8bbdda;
  font-size: 16px;
  line-height: 1.4em;
  padding: 1px 1px 1px 0;
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
.sidebar-row-link-label {
  padding-left: 5px;
}
.sidebar-row-link-label-text {
  overflow: hidden;
  padding-right: 5px;
  text-overflow: ellipsis;
  vertical-align: middle;
  white-space: nowrap;
  width: 180px;
}
.sidebar-section-header {
  margin: 10px 0 5px 0;
}
.section-divider {
  background-color: #4a90e2;
  border: none;
  color: #4a90e2;
  height: 1px;
  margin: 10px 5px 10px 10px;
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
</style>
