<template>
  <div class="default-margins">
    <h1 id="page-header">
      Create {{ domain === 'admitted_students' ? 'CE3' : 'Curated' }} Group
    </h1>
    <BulkAddSids
      :on-bulk-add-sids="bulkAddSids"
      :domain="domain"
      heading-id="page-header"
      id-prefix="curated-group-bulk-add"
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
import {ref} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import CreateCuratedGroupModal from '@/components/curated/CreateCuratedGroupModal'
import BulkAddSids from '@/components/util/BulkAddSids.vue'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {createCuratedGroup} from '@/api/curated'
import {describeCuratedGroupDomain} from '@/lib/berkeley-utils'

const domain = useRoute().query.domain || 'default'
const isSaving = ref(false)
const router = useRouter()
const showCreateModal = ref(false)
const sids = ref(undefined)

const bulkAddSids = data => {
  sids.value = data
  showCreateModal.value = true
}

const cancel = () => {
  showCreateModal.value = false
  isSaving.value = false
  alertScreenReader(`Canceled create ${describeCuratedGroupDomain(domain)}.`)
  putFocusNextTick('btn-curated-group-bulk-add-sids')
}

const create = name => {
  showCreateModal.value = false
  isSaving.value = true
  createCuratedGroup(domain, name, sids.value).then(group => {
    alertScreenReader(`${describeCuratedGroupDomain(domain)} "${name}" created. It has ${sids.value.length} students.`)
    router.push(`/curated/${group.id}`).then(() => {
      isSaving.value = false
    })
  })
}
</script>
