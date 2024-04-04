<template>
  <v-navigation-drawer class="bg-tertiary" permanent>
    <v-list-item v-if="myCohorts" class="list-item" nav>
      <Cohorts class="mt-2" :cohorts="myCohorts" />
    </v-list-item>
    <hr class="mx-2 section-divider" />
    <v-list-item v-if="myCuratedGroups" class="list-item">
      <CuratedGroups domain="default" />
    </v-list-item>
    <hr class="mx-2 section-divider" />
    <v-list-item v-if="canAccessAdmittedStudents" class="list-item">
      <div class="ml-2 sidebar-header">
        Admitted Students
      </div>
      <MyAdmitCohorts v-if="myAdmitCohorts" :cohorts="myAdmitCohorts" />
    </v-list-item>
    <v-list-item v-if="canAccessAdmittedStudents && myCuratedGroups" class="list-item">
      <CuratedGroups v-if="myCuratedGroups" domain="admitted_students" header-class="sidebar-sub-header" />
    </v-list-item>
    <hr class="mx-2 section-divider" />
    <v-list-item class="list-item">
      <div class="sidebar-row-link">
        <router-link
          id="cohorts-all"
          class="ml-1 mr-2"
          to="/cohorts/all"
        >
          Everyone's Cohorts
        </router-link>
      </div>
    </v-list-item>
    <v-list-item class="list-item">
      <div class="sidebar-row-link">
        <router-link
          id="groups-all"
          class="ml-1 mr-2"
          to="/groups/all"
        >
          Everyone's Groups
        </router-link>
      </div>
    </v-list-item>
    <v-list-item v-if="canAccessAdvisingData" class="list-item mt-12">
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
      <EditBatchNoteModal
        initial-mode="createBatch"
        :is-open="isCreateNoteModalOpen"
        :on-close="onCreateNoteModalClose"
        :toggle-show="toggleCreateNoteModal"
      />
    </v-list-item>
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
    canAccessAdmittedStudents: false,
    canAccessAdvisingData: false,
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
  created() {
    this.canAccessAdmittedStudents = get(useContextStore().currentUser, 'canAccessAdmittedStudents')
    this.canAccessAdvisingData = get(useContextStore().currentUser, 'canAccessAdvisingData')
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

<style scoped>
.list-item {
  padding: 0;
  margin-top: 2px;
}
</style>
