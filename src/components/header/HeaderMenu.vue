<template>
  <div class="d-flex justify-space-around">
    <v-menu
      :width="isPeerAdvisingManager(currentUser) ? 360 : 280"
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
      <v-list class="py-3 remove-scroll" variant="flat">
        <v-list-item-action v-if="currentUser.canReadDegreeProgress">
          <v-btn
            id="header-menu-degree-check"
            :aria-current="route.path === '/degrees' ? 'page' : false"
            class="font-size-16 justify-start text-decoration-none w-100"
            color="primary"
            size="large"
            text="Degree Checks"
            to="/degrees"
            variant="text"
          />
        </v-list-item-action>
        <v-list-item-action v-if="isPeerAdvisingManager(currentUser)">
          <!-- TODO: Implement the 'to:' path when peer_advising_department_memberships is wired up. -->
          <v-btn
            id="header-menu-peer-management"
            :aria-current="route.path.startsWith('/peer/management') ? 'page' : false"
            class="font-size-16 justify-start text-decoration-none w-100"
            color="primary"
            size="large"
            text="Peer Advisor Manager Dashboard"
            to="/peer/management/1"
            variant="text"
          />
        </v-list-item-action>
        <v-list-item-action v-if="currentUser.isAdmin || myDirectorDepartment">
          <v-btn
            id="header-menu-analytics"
            :aria-current="route.path.startsWith('/analytics') ? 'page' : false"
            class="font-size-16 justify-start text-decoration-none w-100"
            color="primary"
            size="large"
            text="Flight Data Recorder"
            :to="currentUser.isAdmin ? '/analytics/qcadv' : `/analytics/${myDirectorDepartment.toLowerCase()}`"
            variant="text"
          />
        </v-list-item-action>
        <v-list-item-action v-if="currentUser.isAdmin">
          <v-btn
            id="header-menu-flight-deck"
            :aria-current="route.path === '/admin' ? 'page' : false"
            class="font-size-16 justify-start text-decoration-none w-100"
            color="primary"
            size="large"
            text="Flight Deck"
            to="/admin"
            variant="text"
          />
        </v-list-item-action>
        <v-list-item-action v-if="currentUser.isAdmin">
          <v-btn
            id="header-menu-passengers"
            :aria-current="route.path === '/admin/passengers' ? 'page' : false"
            class="font-size-16 justify-start text-decoration-none w-100"
            color="primary"
            size="large"
            text="Passenger Manifest"
            to="/admin/passengers"
            variant="text"
          />
        </v-list-item-action>
        <v-list-item-action v-if="!currentUser.isAdmin">
          <v-btn
            id="header-menu-profile"
            :aria-current="route.path === '/profile' ? 'page' : false"
            class="font-size-16 justify-start text-decoration-none w-100"
            color="primary"
            size="large"
            text="Profile"
            to="/profile"
            variant="text"
          />
        </v-list-item-action>
        <v-list-item-action>
          <v-btn
            class="font-size-16 font-weight-500 justify-start text-decoration-none w-100"
            color="primary"
            :href="`mailto:${contextStore.config.supportEmailAddress}`"
            size="large"
            target="_blank"
            variant="text"
          >
            Feedback/Help<span class="sr-only">: Email the BOA team (opens in new window)</span>
          </v-btn>
        </v-list-item-action>
        <v-list-item-action>
          <v-btn
            id="header-menu-log-out"
            class="font-size-16 justify-start text-decoration-none w-100"
            color="primary"
            size="large"
            text="Log Out"
            variant="text"
            @click="logOut"
          />
        </v-list-item-action>
      </v-list>
    </v-menu>
  </div>
</template>

<script setup>
import {getCasLogoutUrl} from '@/api/auth'
import {isPeerAdvisingManager, myDeptCodes} from '@/berkeley'
import {mdiMenuDown} from '@mdi/js'
import {reactive, ref} from 'vue'
import {useContextStore} from '@/stores/context'
import {useRoute} from 'vue-router'

const contextStore = useContextStore()
const currentUser = reactive(contextStore.currentUser)
const deptCodes = myDeptCodes(['director'])
const isMenuOpen = ref(false)
const myDirectorDepartment = deptCodes && deptCodes[0]
const route = useRoute()

const logOut = () => getCasLogoutUrl().then(data => window.location.href = data.casLogoutUrl)
</script>

<style scoped>
.header-button-menu {
  height: 46px;
}
.remove-scroll {
  overflow: hidden !important;
}
</style>
