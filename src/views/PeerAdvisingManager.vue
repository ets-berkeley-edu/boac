<template>
  <div v-if="!loading" class="bg-sky-blue">
    <div class="pb-2 pt-4 px-4">
      <h1 id="page-header" class="mr-2">Peer Advising Management Dashboard</h1>
    </div>
    <v-tabs
      v-model="tab"
      aria-label="Peer Advising Management tab"
      :aria-orientation="$vuetify.display.mdAndUp ? 'horizontal' : 'vertical'"
      class="ml-3"
      density="comfortable"
      :direction="$vuetify.display.mdAndUp ? 'horizontal' : 'vertical'"
      :items="tabs"
      mobile-breakpoint="md"
    >
      <template #tab="{item}">
        <v-tab
          :id="`peer-advising-management-tab-${item.key}s`"
          :aria-controls="`peer-advising-management-tab-panel-${item.key}s`"
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
                :id="`peer-advising-management-count-${item.key}s`"
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
          :id="`peer-advising-management-tab-panel-${item.key}s`"
          :aria-labelledby="`peer-advising-management-tab-${item.key}s`"
          :aria-selected="item.key === tab"
          class="bg-white px-4"
          role="tabpanel"
          :value="item.key"
        >
          <div v-if="item.key === 'account'">
            <div class="mb-3 mt-5">
              <h2 class="font-size-16">{{ item.label }}</h2>
            </div>
            <PeerAdvisingAccountMgmt :peer-advising-department="peerAdvisingDepartment" />
          </div>
          <div v-if="item.key === 'templates'" class="pt-3">
            <PeerAdvisingNoteTemplates :peer-advising-department="peerAdvisingDepartment" />
          </div>
          <div v-if="item.key === 'reporting'">
            CCC
          </div>
        </v-tabs-window-item>
      </template>
    </v-tabs>
  </div>
</template>

<script setup>
import PeerAdvisingAccountMgmt from '@/components/peer/PeerAdvisingAccountMgmt'
import PeerAdvisingNoteTemplates from '@/components/peer/PeerAdvisingNoteTemplates'
import {computed, onMounted, ref} from 'vue'
import {getPeerAdvisingDepartment} from '@/api/peer-advising'
import {toInt} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {useRoute} from 'vue-router'

const contextStore = useContextStore()

const loading = computed(() => contextStore.loading)
const peerAdvisingDepartment = ref([])
const tab = ref(undefined)
const tabs = [
  {key: 'account', label: 'Account Management'},
  {key: 'templates', label: 'Note Templates'},
  {key: 'reporting', label: 'Reporting & Statistics'},
]

contextStore.loadingStart()

onMounted(() => {
  const peerAdvisingDeptId = toInt(useRoute().params.id)
  getPeerAdvisingDepartment(peerAdvisingDeptId).then(data => {
    peerAdvisingDepartment.value = data
    contextStore.loadingComplete('Peer Advising Management Dashboard is ready.')
  })
})
</script>
