<template>
  <div class="d-flex justify-space-around" role="navigation">
    <v-menu
      eager
      transition="slide-y-transition"
      variant="link"
      :width="isPeerAdvisorManager(currentUser) ? 320 : 220"
      @update:model-value="isOpen => isMenuOpen = isOpen"
    >
      <template #activator="{ props }">
        <button
          id="header-dropdown-under-name"
          :aria-label="`${currentUser.firstName} quick links`"
          class="v-btn button-menu header-button-menu bg-primary pr-3 text-body-1 text-white"
          :class="{'button-menu-active': isMenuOpen}"
          :title="`User profile for ${currentUser.name || `UID ${currentUser.uid}` }`"
          v-bind="props"
        >
          {{ currentUser.firstName || `UID:${currentUser.uid}` }}
          <v-icon :icon="mdiMenuDown" size="24" />
        </button>
      </template>
      <v-list density="compact">
        <v-list-item v-if="currentUser.canReadDegreeProgress" class="pa-0">
          <v-btn
            id="header-menu-degree-check"
            :aria-current="route.path === '/degrees' ? 'page' : false"
            class="header-menu-item"
            color="primary"
            density="comfortable"
            size="large"
            text="Degree Checks"
            to="/degrees"
            variant="text"
          />
        </v-list-item>
        <v-list-item
          v-for="peerAdvisingDepartment in peerAdvisingDepartments"
          :key="peerAdvisingDepartment.peerAdvisingDepartmentId"
          class="pa-0"
        >
          <v-btn
            v-if="peerAdvisingDepartments.length === 1"
            id="header-menu-peer-management"
            :aria-current="route.path.startsWith('/peer/management') ? 'page' : false"
            class="header-menu-item"
            color="primary"
            density="comfortable"
            size="large"
            text="Peer Advising Manager Dashboard"
            :to="`/peer/management/${peerAdvisingDepartment.peerAdvisingDepartmentId}`"
            variant="text"
          />
          <v-btn
            v-if="peerAdvisingDepartments.length > 1"
            :id="`header-menu-peer-management-${peerAdvisingDepartment.peerAdvisingDepartmentId}`"
            :aria-current="route.path.startsWith(`/peer/management/${peerAdvisingDepartment.peerAdvisingDepartmentId}`) ? 'page' : false"
            class="header-menu-item"
            color="primary"
            density="comfortable"
            size="large"
            :text="`Peer Advising Dashboard: ${peerAdvisingDepartment.name}`"
            :to="`/peer/management/${peerAdvisingDepartment.peerAdvisingDepartmentId}`"
            variant="text"
          />
        </v-list-item>
        <v-list-item v-if="currentUser.isAdmin || myDirectorDepartment" class="pa-0">
          <v-btn
            id="header-menu-analytics"
            :aria-current="route.path.startsWith('/analytics') ? 'page' : false"
            class="header-menu-item"
            color="primary"
            density="comfortable"
            size="large"
            text="Flight Data Recorder"
            :to="currentUser.isAdmin ? '/analytics/qcadv' : `/analytics/${myDirectorDepartment.toLowerCase()}`"
            variant="text"
          />
        </v-list-item>
        <v-list-item v-if="currentUser.isAdmin" class="pa-0">
          <v-btn
            id="header-menu-flight-deck"
            :aria-current="route.path === '/admin' ? 'page' : false"
            class="header-menu-item"
            color="primary"
            density="comfortable"
            size="large"
            text="Flight Deck"
            to="/admin"
            variant="text"
          />
        </v-list-item>
        <v-list-item v-if="currentUser.isAdmin" class="pa-0">
          <v-btn
            id="header-menu-passengers"
            :aria-current="route.path === '/admin/passengers' ? 'page' : false"
            class="header-menu-item"
            color="primary"
            density="comfortable"
            size="large"
            text="Passenger Manifest"
            to="/admin/passengers"
            variant="text"
          />
        </v-list-item>
        <v-list-item v-if="!currentUser.isAdmin" class="pa-0" density="compact">
          <v-btn
            id="header-menu-profile"
            :aria-current="route.path === (isPeerAdvisor(currentUser) ? '/peer_advisor/profile' : '/profile') ? 'page' : false"
            class="header-menu-item"
            color="primary"
            density="comfortable"
            size="large"
            text="Profile"
            to="/profile"
            variant="text"
          />
        </v-list-item>
        <v-list-item class="pa-0">
          <v-btn
            class="header-menu-item font-size-16 font-weight-500 justify-start text-decoration-none w-100"
            color="primary"
            density="comfortable"
            :href="`mailto:${contextStore.config.supportEmailAddress}`"
            size="large"
            target="_blank"
            variant="text"
          >
            Feedback/Help<span class="sr-only">: Email the BOA team (opens in new tab)</span>
          </v-btn>
        </v-list-item>
        <v-list-item class="pa-0">
          <v-btn
            id="header-menu-log-out"
            class="header-menu-item"
            color="primary"
            density="comfortable"
            size="large"
            text="Log Out"
            variant="text"
            @click="logOut"
          />
        </v-list-item>
      </v-list>
    </v-menu>
  </div>
</template>

<script setup>
import {mdiMenuDown} from '@mdi/js'
import {onMounted, ref} from 'vue'
import {useRoute} from 'vue-router'
import {alertScreenReader} from '@/lib/utils'
import {getCasLogoutUrl} from '@/api/auth'
import {isPeerAdvisor, isPeerAdvisorManager} from '@/lib/boa-user'
import {getPeerAdvisorDepartmentMemberships, myDeptCodes} from '@/lib/berkeley-department'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const deptCodes = myDeptCodes(['director'])
const isMenuOpen = ref(false)
const myDirectorDepartment = deptCodes && deptCodes[0]
const peerAdvisingDepartments = ref()
const route = useRoute()

onMounted(() => {
  peerAdvisingDepartments.value = getPeerAdvisorDepartmentMemberships(currentUser, 'peer_advisor_manager')
})

const logOut = () => {
  alertScreenReader('BOA: signing out.')
  getCasLogoutUrl().then(data => window.location.href = data.casLogoutUrl)
}
</script>

<style lang="scss" scoped>
.header-button-menu {
  height: 46px;
  &::after {
    outline-style: solid;
    outline-width: 0.125rem;
  }
}
.header-menu-item {
  border-radius: 0;
  font-size: 16px;
  letter-spacing: normal;
  justify-content: start;
  text-decoration-line: none;
  width: 100%;
}
</style>
