<template>
  <div class="default-margins">
    <h1 class="page-section-header">Create {{ domain === 'admitted_students' ? 'CE3' : 'Curated' }} Group</h1>
    <div>
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
      :show-modal="showCreateModal"
    />
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import CreateCuratedGroupModal from '@/components/curated/CreateCuratedGroupModal'
import CuratedGroupBulkAdd from '@/components/curated/CuratedGroupBulkAdd.vue'
import Util from '@/mixins/Util'
import {alertScreenReader} from '@/lib/utils'
import {createCuratedGroup} from '@/api/curated'
import {describeCuratedGroupDomain} from '@/berkeley'

export default {
  name: 'CreateCuratedGroup',
  components: {CreateCuratedGroupModal, CuratedGroupBulkAdd},
  mixins: [Context, Util],
  data: () => ({
    domain: undefined,
    isSaving: false,
    showCreateModal: false,
    sids: undefined
  }),
  created() {
    this.domain = this.$route.query.domain || 'default'
    this.loadingComplete()
  },
  methods: {
    bulkAddSids(sids) {
      this.isSaving = true
      this.sids = sids
      this.showCreateModal = true
    },
    cancel() {
      this.showCreateModal = false
      this.isSaving = false
      alertScreenReader(`You have canceled the operation to create a new ${describeCuratedGroupDomain(this.domain)}.`)
      this.putFocusNextTick('curated-group-bulk-add-sids')
    },
    create(name) {
      this.showCreateModal = false
      createCuratedGroup(this.domain, name, this.sids)
        .then(group => {
          alertScreenReader(`Curated group '${name}' created. It has ${this.sids.length} students.`)
          this.isSaving = false
          this.$router.push(`/curated/${group.id}`)
        })
    }
  }
}
</script>
