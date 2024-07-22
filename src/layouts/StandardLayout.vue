<template>
  <v-fade-transition>
    <div class="vh-100">
      <a id="skip-to-content-link" href="#content" class="sr-only">Skip to main content</a>
      <v-layout>
        <v-app-bar
          color="primary"
          elevation="0"
          @shortkey="() => putFocusNextTick('search-students-input')"
        >
          <AppBar />
        </v-app-bar>
        <v-navigation-drawer
          class="bg-tertiary pt-1 sidebar"
          permanent
          :rail="$vuetify.display.smAndDown"
          rail-width="200"
        >
          <template #append>
            <div
              v-if="currentUser.canAccessAdvisingData"
              class="fixed-bottom-sidebar bg-tertiary px-3 py-0 w-100"
              :class="{'z-index-0': !loading}"
            >
              <LinkToDraftNotes class="pt-2" />
              <v-btn
                v-if="!currentUser.isAdmin"
                id="batch-note-button"
                class="mb-5 mt-3 w-100"
                color="primary"
                :disabled="!!useNoteStore().mode"
                variant="flat"
                @click="isCreateNoteModalOpen = true"
              >
                <v-icon class="mr-1" :icon="mdiFileDocument" />
                New Note
              </v-btn>
              <EditBatchNoteModal
                v-model="isCreateNoteModalOpen"
                initial-mode="createBatch"
                :on-close="() => {
                  isCreateNoteModalOpen = false
                  putFocusNextTick('batch-note-button')
                }"
                :toggle-show="show => isCreateNoteModalOpen = show"
              />
            </div>
          </template>
          <Sidebar />
        </v-navigation-drawer>
        <v-main id="content">
          <div :class="{'align-center d-flex justify-center': loading}">
            <PlaneGoRound v-if="loading" />
            <div v-show="!loading" class="h-100 w-100">
              <ServiceAnnouncement />
              <router-view :key="split($route.fullPath, '#', 1)[0]" />
            </div>
          </div>
          <v-footer
            v-if="!loading"
            absolute
            class="w-100"
            color="transparent"
            location="bottom"
          >
            <AppFooter />
          </v-footer>
        </v-main>
      </v-layout>
    </div>
  </v-fade-transition>
</template>

<script setup>
import AppBar from '@/layouts/shared/AppBar'
import AppFooter from '@/layouts/shared/AppFooter'
import EditBatchNoteModal from '@/components/note/EditBatchNoteModal.vue'
import LinkToDraftNotes from '@/components/sidebar/LinkToDraftNotes.vue'
import PlaneGoRound from '@/layouts/shared/PlaneGoRound.vue'
import ServiceAnnouncement from '@/layouts/shared/ServiceAnnouncement'
import Sidebar from '@/components/sidebar/Sidebar'
import {mdiFileDocument} from '@mdi/js'
import {putFocusNextTick} from '@/lib/utils'
import {ref} from 'vue'
import {split} from 'lodash'
import {storeToRefs} from 'pinia'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

const currentUser = useContextStore().currentUser
const {loading} = storeToRefs(useContextStore())
const isCreateNoteModalOpen = ref(false)

putFocusNextTick('home-header')
</script>

<style scoped>
.fixed-bottom-sidebar {
  bottom: 0;
  box-shadow: 0px -25px 35px -22px rgb(var(--v-theme-tertiary));
  position: fixed;
  z-index: 2;
}
</style>

<style>
.sidebar .v-navigation-drawer__content {
  scrollbar-width: none;
}
</style>
