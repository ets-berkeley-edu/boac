<template>
  <div class="d-flex justify-space-around">
    <v-menu
      :width="isPeerAdvisorManager(currentUser) ? 360 : 280"
      transition="slide-y-transition"
      variant="link"
      @update:model-value="isOpen => isMenuOpen = isOpen"
    >
      <template #activator="{ props }">
        <button
          id="header-dropdown-under-name"
          class="button-menu header-button-menu bg-primary pr-3 text-body-1 text-white"
          :class="{'button-menu-active': isMenuOpen}"
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
            class="font-size-16 justify-start text-decoration-none w-100"
            color="primary"
            text="Degree Checks"
            to="/degrees"
            variant="text"
          />
        </v-list-item>
        <v-list-item v-if="isPeerAdvisorManager(currentUser)" class="pa-0">
          <v-btn
            id="header-menu-peer-management"
            :aria-current="route.path.startsWith('/peer/management') ? 'page' : false"
            class="font-size-16 justify-start text-decoration-none w-100"
            color="primary"
            density="comfortable"
            size="large"
            text="Peer Advisor Manager Dashboard"
            :to="`/peer/management/${peerAdvisingDepartmentId}`"
            variant="text"
          />
        </v-list-item>
        <v-list-item v-if="currentUser.isAdmin || myDirectorDepartment" class="pa-0">
          <v-btn
            id="header-menu-analytics"
            :aria-current="route.path.startsWith('/analytics') ? 'page' : false"
            class="font-size-16 justify-start text-decoration-none w-100"
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
            class="font-size-16 justify-start text-decoration-none w-100"
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
            class="font-size-16 justify-start text-decoration-none w-100"
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
            :aria-current="route.path === '/profile' ? 'page' : false"
            class="font-size-16 justify-start text-decoration-none w-100"
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
            class="font-size-16 font-weight-500 justify-start text-decoration-none w-100"
            color="primary"
            density="comfortable"
            :href="`mailto:${contextStore.config.supportEmailAddress}`"
            size="large"
            target="_blank"
            variant="text"
          >
            Feedback/Help<span class="sr-only">: Email the BOA team (opens in new window)</span>
          </v-btn>
        </v-list-item>
        <v-list-item class="pa-0">
          <v-btn
            id="header-menu-log-out"
            class="font-size-16 justify-start text-decoration-none w-100"
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
import {each, find, get} from 'lodash'
import {mdiMenuDown} from '@mdi/js'
import {onMounted, ref} from 'vue'
import {useRoute} from 'vue-router'
import {getCasLogoutUrl} from '@/api/auth'
import {isPeerAdvisorManager} from '@/lib/boa-user'
import {myDeptCodes} from '@/lib/berkeley-department'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const deptCodes = myDeptCodes(['director'])
const isMenuOpen = ref(false)
const myDirectorDepartment = deptCodes && deptCodes[0]
const route = useRoute()
const peerAdvisingDepartmentId = ref(NaN)

onMounted(() => {
  each(currentUser.departments, department => {
    const peerAdvisingDepartment = find(department.memberships, 'peerAdvisingDepartmentId')
    peerAdvisingDepartmentId.value = get(peerAdvisingDepartment, 'peerAdvisingDepartmentId')
    return !!peerAdvisingDepartmentId.value
  })
})

const logOut = () => getCasLogoutUrl().then(data => window.location.href = data.casLogoutUrl)
</script>

<style scoped>
.header-button-menu {
  height: 46px;
}
</style>
