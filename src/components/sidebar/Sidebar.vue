<template>
  <v-navigation-drawer
    class="sidebar"
    color="tertiary"
    permanent
    :scrim="false"
  >
    <div class="bg-tertiary pt-3">
      <div aria-label="Cohorts and Curated Groups">
        <div v-if="myCohorts">
          <Cohorts :cohorts="myCohorts" />
          <hr class="ml-2 mr-2 section-divider" />
        </div>
        <div v-if="myCuratedGroups">
          <CuratedGroups domain="default" />
          <hr class="ml-2 mr-2 section-divider" />
        </div>
        <div v-if="get(useContextStore().currentUser, 'canAccessAdmittedStudents')">
          <div class="ml-2 sidebar-header">
            Admitted Students
          </div>
          <div class="ml-1">
            <div v-if="myAdmitCohorts" class="py-2">
              <MyAdmitCohorts :cohorts="myAdmitCohorts" />
            </div>
            <div v-if="myCuratedGroups">
              <div class="pt-2">
                <CuratedGroups domain="admitted_students" header-class="sidebar-sub-header" />
              </div>
            </div>
          </div>
          <hr class="mx-2 section-divider" />
        </div>
        <div class="mb-2 px-1 sidebar-row-link">
          <router-link id="cohorts-all" to="/cohorts/all">Everyone's Cohorts</router-link>
        </div>
        <div class="mb-2 px-1 sidebar-row-link">
          <router-link id="groups-all" to="/groups/all">Everyone's Groups</router-link>
        </div>
      </div>
      <v-banner
        v-if="get(useContextStore().currentUser, 'canAccessAdvisingData')"
        aria-label="Notes"
        :border="'tertiary'"
        class="sidebar-sticky bg-tertiary px-0 py-3"
        sticky
      >
        <div class="d-flex flex-column w-100">
          <LinkToDraftNotes />
          <v-btn
            v-if="!get(useContextStore().currentUser, 'isAdmin')"
            id="batch-note-button"
            class="mx-3 mt-1"
            color="primary"
            :disabled="!!useNoteStore().mode"
            variant="flat"
            @click="isCreateNoteModalOpen = true"
          >
            <v-icon class="mr-1" :icon="mdiFileDocument" />
            New Note
          </v-btn>
        </div>
        <EditBatchNoteModal
          initial-mode="createBatch"
          :is-open="isCreateNoteModalOpen"
          :on-close="onCreateNoteModalClose"
          :toggle-show="toggleCreateNoteModal"
        />
      </v-banner>
    </div>
  </v-navigation-drawer>
</template>

<script setup>
import {mdiFileDocument} from '@mdi/js'
</script>

<script>
import Cohorts from '@/components/sidebar/Cohorts.vue'
import CuratedGroups from '@/components/sidebar/CuratedGroups.vue'
import EditBatchNoteModal from '@/components/note/EditBatchNoteModal.vue'
import LinkToDraftNotes from '@/components/sidebar/LinkToDraftNotes.vue'
import MyAdmitCohorts from '@/components/sidebar/MyAdmitCohorts.vue'
import {get, filter} from 'lodash'
import {putFocusNextTick} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

export default {
  name: 'Sidebar',
  components: {
    Cohorts,
    CuratedGroups,
    EditBatchNoteModal,
    LinkToDraftNotes,
    MyAdmitCohorts
  },
  data: () => ({
    isCreateNoteModalOpen: false
  }),
  computed: {
    myAdmitCohorts() {
      return filter(get(useContextStore().currentUser, 'myCohorts'), ['domain', 'admitted_students'])
    },
    myCohorts() {
      return filter(get(useContextStore().currentUser, 'myCohorts'), ['domain', 'default'])
    },
    myCuratedGroups() {
      return get(useContextStore().currentUser, 'myCuratedGroups')
    }
  },
  methods: {
    get,
    onCreateNoteModalClose() {
      this.isCreateNoteModalOpen = false
      putFocusNextTick('batch-note-button')
    },
    toggleCreateNoteModal(show) {
      this.isCreateNoteModalOpen = show
    },
    useNoteStore
  }
}
</script>

<style>
.sidebar.v-navigation-drawer .v-navigation-drawer__content {
  overflow: unset !important;
}
.sidebar-sticky {
  bottom: 0px;
  box-shadow: 0px -20px 30px -15px rgba(var(--v-theme-tertiary), 0.7);
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
  background-color: rgb(var(--v-theme-secondary));
  border-radius: 10px;
  color: rgb(var(--v-theme-quaternary));
  display: inline-block;
  font-size: 16px;
  font-weight: 800;
  height: 20px;
  line-height: 20px;
  padding: 0 4px 0 4px;
  text-align: center;
}
.sidebar-row-link {
  border-left: 6px solid transparent;
  color: rgb(var(--v-theme-secondary));
  font-size: 16px;
  line-height: 24px;
}
.sidebar-row-link:hover,
.sidebar-row-link:focus,
.sidebar-row-link:focus-within,
.sidebar-row-link:active {
  background-color: rgb(var(--v-theme-quaternary));
  border: 0;
  border-left: 6px solid rgb(var(--v-theme-warning)) !important;
  color: rgb(var(--v-theme-warning));
  text-decoration: none;
  outline-style: none;
}
.sidebar-row-link:hover .sidebar-pill,
.sidebar-row-link:focus .sidebar-pill,
.sidebar-row-link:focus-within .sidebar-pill,
.sidebar-row-link:active .sidebar-pill {
  background-color: rgb(var(--v-theme-warning));
}
.sidebar-row-link a:link,
.sidebar-row-link a:visited {
  text-decoration: none;
  border: 0;
  color: inherit;
  outline-style: none;
}
</style>
