<template>
  <div>
    <b-dropdown
      id="header-dropdown-under-name"
      class="mr-2"
      variant="link"
      no-caret
      right
    >
      <template slot="button-content">
        <div class="d-flex align-items-center">
          <div class="b-link-text">{{ $currentUser.firstName || `UID:${$currentUser.uid}` }}</div><font-awesome icon="caret-down" class="ml-1 b-link-text" />
        </div>
      </template>
      <b-dropdown-item
        v-if="$currentUser.isAdmin || myDirectorDepartment"
        id="header-menu-analytics"
        :to="$currentUser.isAdmin ? '/analytics/qcadv' : `/analytics/${myDirectorDepartment.toLowerCase()}`"
        class="nav-link-color text-decoration-none"
      >
        Flight Data Recorder
      </b-dropdown-item>
      <b-dropdown-item
        v-if="$currentUser.isAdmin"
        id="header-menu-flight-deck"
        class="nav-link-color text-decoration-none"
        to="/admin"
      >
        Flight Deck
      </b-dropdown-item>
      <b-dropdown-item
        v-if="$currentUser.isAdmin"
        id="header-menu-passengers"
        to="/admin/passengers"
        class="nav-link-color text-decoration-none"
      >
        Passenger Manifest
      </b-dropdown-item>
      <b-dropdown-item
        v-if="!$currentUser.isAdmin"
        id="header-menu-profile"
        class="nav-link-color text-decoration-none"
        :to="isSimplyScheduler($currentUser) ? '/scheduler/profile' : '/profile'"
      >
        Profile
      </b-dropdown-item>
      <b-dropdown-item
        v-if="degreeCheckEnabled"
        id="header-menu-degree-check"
        class="nav-link-color text-decoration-none"
        to="/degrees"
      >
        Degree Checks
      </b-dropdown-item>
      <b-dropdown-item
        :href="`mailto:${$config.supportEmailAddress}`"
        target="_blank"
        aria-label="Send email to the BOA team"
      >
        Feedback/Help<span class="sr-only"> (new browser tab will open)</span>
      </b-dropdown-item>
      <b-dropdown-item href="#" @click="logOut">Log Out</b-dropdown-item>
    </b-dropdown>
  </div>
</template>

<script>
import Berkeley from '@/mixins/Berkeley'
import Context from '@/mixins/Context'
import CurrentUserExtras from '@/mixins/CurrentUserExtras'
import Util from '@/mixins/Util'
import {getCasLogoutUrl} from '@/api/auth'

export default {
  name: 'HeaderMenu',
  mixins: [Berkeley, Context, CurrentUserExtras, Util],
  data: () => ({
    myDirectorDepartment: undefined
  }),
  created() {
    const deptCodes = this.myDeptCodes(['director'])
    this.myDirectorDepartment = deptCodes && deptCodes[0]
  },
  methods: {
    logOut: () => getCasLogoutUrl().then(data => window.location.href = data.casLogoutUrl)
  }
}
</script>

<style scoped>
.b-link-text {
  color: #fff;
}
.nav-link-color {
  color: #212529;
}
</style>
