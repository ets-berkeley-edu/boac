<template>
  <div v-if="!loading" class="bg-sky-blue">
    <div class="pb-2 pt-4 px-4">
      <h1 id="page-header" :class="{'mb-1': currentUser.isAdmin}" class="mr-2">Peer Advising Management Dashboard</h1>
      <div v-if="currentUser.isAdmin && peerAdvisingDepartment" class="mb-1">
        <span class="font-weight-bold text-medium-emphasis">{{ peerAdvisingDepartment.name }}</span><span v-if="peerAdvisingDepartment.name !== peerAdvisingDepartment.universityDeptName">,
          within {{ peerAdvisingDepartment.universityDeptName }}.
        </span>
      </div>
    </div>
    <v-tabs
      v-model="tab"
      aria-label="Peer Advising Management tab"
      :aria-orientation="mdAndUp ? 'horizontal' : 'vertical'"
      class="ml-3"
      density="comfortable"
      :direction="mdAndUp ? 'horizontal' : 'vertical'"
      :items="tabs"
      mobile-breakpoint="md"
    >
      <template #tab="{item}">
        <v-tab
          :id="`peer-advising-management-tab-${item.key}`"
          :aria-controls="`peer-advising-management-tab-panel-${item.key}`"
          class="border-s-sm border-e-sm border-t-sm mx-1 rounded-t-lg"
          :class="{
            'bg-white border-b-0': item.key === tab,
            'bg-grey-lighten-4 border-b-md': item.key !== tab
          }"
          hide-slider
          min-width="120"
          :value="item.key"
          variant="text"
        >
          <template #default>
            <div class="font-size-12 font-weight-bold">
              <div
                :id="`peer-advising-management-count-${item.key}`"
                class="text-uppercase"
                :class="{'text-primary': item.key === tab, 'text-black': item.key !== tab}"
                v-html="item.label"
              />
            </div>
          </template>
        </v-tab>
      </template>
      <template #item="{item}">
        <v-tabs-window-item
          :id="`peer-advising-management-tab-panel-${item.key}`"
          :aria-labelledby="`peer-advising-management-tab-${item.key}`"
          :aria-selected="item.key === tab"
          class="bg-white px-4"
          role="tabpanel"
          :value="item.key"
        >
          <div v-if="item.key === 'accounts'" class="mt-3 mr-12">
            <PeerAdvisingAccountMgmt
              v-if="peerAdvisingDepartment"
              :is-refreshing="isRefreshing"
              :peer-advising-department="peerAdvisingDepartment"
              :peer-advisors="_filter(peerAdvisingDepartment.peerAdvisingDepartmentMembers, ['role', 'peer_advisor'])"
              :refresh="reloadPeerAdvisingDepartment"
            />
          </div>
          <div v-if="item.key === 'templates'" class="pt-3">
            <PeerAdvisingNoteTemplates
              v-if="peerAdvisingDepartment"
              :peer-advising-department="peerAdvisingDepartment"
            />
          </div>
          <div v-if="item.key === 'reporting'" class="pt-3">
            <PeerAdvisorManagerReports
              v-if="peerAdvisingDepartment"
              :peer-advising-department="peerAdvisingDepartment"
            />
          </div>
          <div v-if="item.key === 'dashboard'" class="pt-3">
            <PeerAdvisorDashboardView
              v-if="peerAdvisingDepartment"
              :peer-advising-department="peerAdvisingDepartment"
            />
          </div>
        </v-tabs-window-item>
      </template>
    </v-tabs>
  </div>
</template>

<script setup lang="ts">
import {computed, onBeforeUnmount, onMounted, ref, watch} from 'vue'
import {filter as _filter, get, includes, map, replace, toLower, toString} from 'lodash'
import {useDisplay} from 'vuetify'
import {useRoute, useRouter} from 'vue-router'
import type {BoaUser, PeerAdvisingDepartment} from '@/lib/types'
import PeerAdvisorDashboardView from '@/components/peer/PeerAdvisorDashboardView.vue'
import PeerAdvisingAccountMgmt from '@/components/peer/PeerAdvisingAccountMgmt.vue'
import PeerAdvisingNoteTemplates from '@/components/peer/PeerAdvisingNoteTemplates.vue'
import PeerAdvisorManagerReports from '@/components/peer/reports/PeerAdvisorManagerReports.vue'
import {getPeerAdvisingDepartment} from '@/api/peer-advising-users'
import {toInt} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const currentUser: BoaUser = contextStore.currentUser
const isRefreshing = ref(false)
const loading = computed(() => contextStore.loading)
const peerAdvisingDepartment = ref<PeerAdvisingDepartment>()
const route = useRoute()
const router = useRouter()
const tab = ref<string>('accounts')
const tabs = [
  {key: 'accounts', label: 'Account Management'},
  {key: 'templates', label: 'Note Templates'},
  {key: 'reporting', label: 'Reporting & Statistics'},
  {key: 'dashboard', label: 'Peer Dashboard View'},
]
const {mdAndUp} = useDisplay()

contextStore.loadingStart()

watch(tab, value => onTabChange(value))

onBeforeUnmount(() => contextStore.removeEventHandler('note-deleted'))

onMounted(() => {
  const hash = replace(route.hash, '#', '')
  onTabChange(toLower(toString(hash)))
  reloadPeerAdvisingDepartment().then(() => {
    contextStore.loadingComplete()
  })
  contextStore.setEventHandler('note-deleted', refresh)
})

const onTabChange = (value: string) => {
  tab.value = includes(map(tabs, 'key'), value) ? value : tab.value
  router.replace({hash: `#${tab.value}`})
}
const reloadPeerAdvisingDepartment = async () => {
  isRefreshing.value = true
  return refresh().then(() => isRefreshing.value = false)
}

const refresh = async () => {
  const peerAdvisingDeptId: string = toString(get(route.params, 'id'))
  return getPeerAdvisingDepartment(
    toInt(peerAdvisingDeptId),
    'peer_advisor',
    true,
    true
  ).then(data => {
    peerAdvisingDepartment.value = data
  })
}
</script>
