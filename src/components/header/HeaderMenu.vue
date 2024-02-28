<template>
  <div>
    <v-menu
      id="header-dropdown-under-name"
      variant="link"
      no-caret
      right
    >
      <template #activator="{ props }">
        <v-btn
          :append-icon="mdiMenuDown"
          color="white"
          v-bind="props"
          variant="text"
        >
          {{ currentUser.firstName || `UID:${currentUser.uid}` }}
        </v-btn>
      </template>
      <v-list class="pt-3">
        <v-list-item-action v-if="currentUser.canReadDegreeProgress">
          <v-btn
            id="header-menu-degree-check"
            class="nav-link-color text-decoration-none"
            to="/degrees"
            variant="text"
          >
            Degree Checks
          </v-btn>
        </v-list-item-action>
        <v-list-item-action v-if="currentUser.isAdmin || myDirectorDepartment">
          <v-btn
            id="header-menu-analytics"
            :to="currentUser.isAdmin ? '/analytics/qcadv' : `/analytics/${myDirectorDepartment.toLowerCase()}`"
            class="nav-link-color text-decoration-none"
            variant="text"
          >
            Flight Data Recorder
          </v-btn>
        </v-list-item-action>
        <v-list-item-action v-if="currentUser.isAdmin">
          <v-btn
            id="header-menu-flight-deck"
            class="nav-link-color text-decoration-none"
            to="/admin"
            variant="text"
          >
            Flight Deck
          </v-btn>
        </v-list-item-action>
        <v-list-item-action v-if="currentUser.isAdmin">
          <v-btn
            id="header-menu-passengers"
            class="nav-link-color text-decoration-none"
            to="/admin/passengers"
            variant="text"
          >
            Passenger Manifest
          </v-btn>
        </v-list-item-action>
        <v-list-item-action
          v-if="!currentUser.isAdmin"
        >
          <v-btn
            id="header-menu-profile"
            class="nav-link-color text-decoration-none"
            to="/profile"
            variant="text"
          >
            Profile
          </v-btn>
        </v-list-item-action>
        <v-list-item-action>
          <v-btn
            aria-label="Send email to the BOA team"
            :href="`mailto:${config.supportEmailAddress}`"
            target="_blank"
            variant="text"
          >
            Feedback/Help<span class="sr-only"> (new browser tab will open)</span>
          </v-btn>
        </v-list-item-action>
        <v-list-item-action>
          <v-btn
            id="header-menu-log-out"
            href="#"
            variant="text"
            @click="logOut"
          >
            Log Out
          </v-btn>
        </v-list-item-action>
      </v-list>
    </v-menu>
  </div>
</template>

<script setup>
import {mdiMenuDown} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import {getCasLogoutUrl} from '@/api/auth'
import {myDeptCodes} from '@/berkeley'

export default {
  name: 'HeaderMenu',
  mixins: [Context, Util],
  data: () => ({
    myDirectorDepartment: undefined
  }),
  created() {
    const deptCodes = myDeptCodes(['director'])
    this.myDirectorDepartment = deptCodes && deptCodes[0]
  },
  methods: {
    logOut: () => getCasLogoutUrl().then(data => window.location.href = data.casLogoutUrl)
  }
}
</script>

<style scoped>
.nav-link-color {
  color: #212529;
}
</style>
