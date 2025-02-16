<template>
  <div class="align-center d-flex">
    <div class="align-center d-flex">
      <div class="quick-links-label">
        Quick links:
      </div>
      <div>
        <v-btn
          id="quick-link-ce3-advisors"
          class="font-size-16 px-2"
          color="primary"
          :disabled="disabled"
          text="CE3"
          variant="text"
          @click="onClickQuickLink('ZCEEE')"
        />
      </div>
      <div>
        |
      </div>
      <div>
        <v-btn
          id="quick-link-coe-advisors"
          class="font-size-16 px-2"
          color="primary"
          :disabled="disabled"
          exact
          text="CoE Advisors"
          variant="text"
          @click="onClickQuickLink('COENG')"
        />
      </div>
      <div>
        |
      </div>
      <div>
        <v-btn
          id="quick-link-qcadv-advisors"
          class="font-size-16 px-2"
          color="primary"
          :disabled="disabled"
          exact
          text="L&amp;S Advisors"
          variant="text"
          @click="onClickQuickLink('QCADV')"
        />
      </div>
      <div>
        |
      </div>
      <div>
        <v-btn
          id="quick-link-peer-advisors"
          class="font-size-16 px-2"
          color="primary"
          :disabled="disabled"
          exact
          text="Peer Advisors"
          variant="text"
          @click="() => onClickPeerAdvisingQuickLink('peer_advisor')"
        />
      </div>
      <div>
        |
      </div>
      <div>
        <v-btn
          id="quick-link-peer-advisor_managers"
          class="font-size-16 px-2"
          color="primary"
          :disabled="disabled"
          exact
          text="Peer Advisor Managers"
          variant="text"
          @click="() => onClickPeerAdvisingQuickLink('peer_advisor_manager')"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {storeToRefs} from 'pinia'
import {useManifestStore} from '@/stores/manifest'

const props = defineProps({
  fetchUsers: {
    required: true,
    type: Function
  }
})

const manifestStore = useManifestStore()
const {disabled} = storeToRefs(manifestStore)

const onClickPeerAdvisingQuickLink = (role: string) => {
  manifestStore.setIsFetching(true)
  manifestStore.setFilter({
    deptCode: undefined,
    peerAdvisingDepartmentId: undefined,
    role,
    searchPhrase: '',
    status: 'active',
    type: 'filter'
  })
  props.fetchUsers()
}

const onClickQuickLink = (deptCode: string) => {
  manifestStore.setFilter({
    deptCode,
    peerAdvisingDepartmentId: undefined,
    role: 'advisor',
    searchPhrase: '',
    status: 'active',
    type: 'filter'
  })
  props.fetchUsers()
}
</script>

<style scoped>
.quick-links-label {
  font-size: 18px;
  font-weight: 600;
  padding-bottom: 1px;
}
</style>
