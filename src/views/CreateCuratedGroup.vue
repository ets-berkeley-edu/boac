<template>
  <div class="default-margins">
    <h1 id="page-header">
      Create {{ domain === 'admitted_students' ? 'CE3' : 'Curated' }} Group
    </h1>
    <div id="page-description">
      Type or paste a list of Student Identification (SID) numbers below. Example: 9999999990, 9999999991
    </div>
    <CuratedGroupBulkAdd
      :bulk-add-sids="bulkAddSids"
      :domain="domain"
      :is-saving="isSaving"
    />
    <CreateCuratedGroupModal
      :cancel="cancel"
      :create="create"
      :domain="domain"
      :is-saving="isSaving"
      :show-modal="showCreateModal"
    />
  </div>
</template>

<script setup>
import CreateCuratedGroupModal from '@/components/curated/CreateCuratedGroupModal'
import CuratedGroupBulkAdd from '@/components/curated/CuratedGroupBulkAdd.vue'
import router from '@/router'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {createCuratedGroup} from '@/api/curated'
import {describeCuratedGroupDomain} from '@/berkeley'
import {ref} from 'vue'
import {useRoute} from 'vue-router'

const domain = useRoute().query.domain || 'default'
const isSaving = ref(false)
const showCreateModal = ref(false)
const sids = ref(undefined)

const bulkAddSids = data => {
  sids.value = data
  showCreateModal.value = true
}

const cancel = () => {
  showCreateModal.value = false
  isSaving.value = false
  alertScreenReader(`You have canceled the operation to create a new ${describeCuratedGroupDomain(domain)}.`)
  putFocusNextTick('curated-group-bulk-add-sids')
}

const create = name => {
  isSaving.value = true
  createCuratedGroup(domain, name, sids.value).then(group => {
    alertScreenReader(`Curated group '${name}' created. It has ${sids.value.length} students.`)
    router.push(`/curated/${group.id}`).then(() => {
      showCreateModal.value = false
      isSaving.value = false
    })
  })
}
</script>
