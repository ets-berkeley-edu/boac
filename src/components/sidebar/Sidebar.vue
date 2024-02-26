<template>
  <div class="pt-3">
    <div role="navigation" aria-label="Cohorts and Curated Groups">
      <div v-if="myCohorts">
        <Cohorts :cohorts="myCohorts" />
        <hr class="ml-2 mr-2 section-divider" />
      </div>
      <div v-if="currentUser.myCuratedGroups">
        <CuratedGroups domain="default" />
        <hr class="ml-2 mr-2 section-divider" />
      </div>
      <div v-if="currentUser.canAccessAdmittedStudents">
        <div class="ml-2 sidebar-header">
          Admitted Students
        </div>
        <div class="ml-1">
          <div v-if="myAdmitCohorts" class="py-2">
            <MyAdmitCohorts :cohorts="myAdmitCohorts" />
          </div>
          <div v-if="currentUser.myCuratedGroups">
            <div class="pt-2">
              <CuratedGroups domain="admitted_students" header-class="sidebar-sub-header" />
            </div>
          </div>
        </div>
        <hr class="mx-2 section-divider" />
      </div>
      <div class="mb-2 sidebar-row-link">
        <div class="ml-1 mr-2">
          <router-link id="cohorts-all" to="/cohorts/all">Everyone's Cohorts</router-link>
        </div>
      </div>
      <div class="mb-2 sidebar-row-link">
        <div class="ml-1 mr-2">
          <router-link id="groups-all" to="/groups/all">Everyone's Groups</router-link>
        </div>
      </div>
    </div>
    <div
      v-if="currentUser.canAccessAdvisingData"
      class="batch-note-button fixed-bottom-sidebar"
      :class="{'z-index-0': !loading}"
    >
      <div class="sidebar" :class="{'mb-3': currentUser.isAdmin}">
        <LinkToDraftNotes />
      </div>
      <div
        v-if="!currentUser.isAdmin"
        class="d-flex justify-content-center mb-3 pl-3 sidebar"
      >
        <b-btn
          id="batch-note-button"
          :disabled="!!mode"
          class="btn-primary-color-override btn-primary-color-override-opaque mr-2 mt-1 w-100"
          variant="primary"
          @click="isCreateNoteModalOpen = true"
        >
          <span class="m-1">
            <font-awesome class="mr-2" icon="file-alt" />
            New Note
          </span>
        </b-btn>
      </div>
    </div>
  </div>
</template>

<script>
import Cohorts from '@/components/sidebar/Cohorts.vue'
import Context from '@/mixins/Context'
import CuratedGroups from '@/components/sidebar/CuratedGroups.vue'
import LinkToDraftNotes from '@/components/sidebar/LinkToDraftNotes.vue'
import MyAdmitCohorts from '@/components/sidebar/MyAdmitCohorts.vue'
import Util from '@/mixins/Util.vue'

export default {
  name: 'Sidebar',
  components: {
    Cohorts,
    CuratedGroups,
    LinkToDraftNotes,
    MyAdmitCohorts
  },
  mixins: [Context, Util],
  data: () => ({
    isCreateNoteModalOpen: false
  }),
  computed: {
    myAdmitCohorts() {
      return this._filter(this.currentUser.myCohorts, ['domain', 'admitted_students'])
    },
    myCohorts() {
      return this._filter(this.currentUser.myCohorts, ['domain', 'default'])
    }
  },
  methods: {
    onCreateNoteModalClose() {
      this.isCreateNoteModalOpen = false
      this.putFocusNextTick('batch-note-button')
    }
  }
}
</script>

<style>
.batch-note-button {
  background-color: rgb(18, 80, 116);
  padding-top: 10px;
  width: 16.6%;
}
.fixed-bottom-sidebar {
  bottom: 0;
  position: fixed;
  z-index: 2;
}
.sidebar-header {
  color: #fff;
  font-size: 16px;
  font-weight: 800;
}
.sidebar-sub-header {
  color: #fff;
  font-size: 15px;
  font-weight: 600;
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
