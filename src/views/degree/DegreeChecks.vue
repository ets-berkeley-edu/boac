<template>
  <div class="ml-3 mr-3 mt-3">
    <Spinner />
    <div v-if="!loading">
      <h1 class="page-section-header pl-1">
        Managing Degree Checks
      </h1>
      <div class="pb-3">
        <router-link
          v-if="$currentUser.canEditDegreeProgress"
          id="degree-check-create-link"
          class="d-flex flex-row-reverse justify-content-end"
          to="/degree/new"
        >
          Create new degree check
          <font-awesome icon="plus" class="m-1" />
        </router-link>
      </div>
      <div v-if="degreeChecks.length">
        <b-table-lite
          id="degree-checks-table"
          :fields="[
            {key: 'name', label: 'Degree Check', tdClass: 'align-middle'},
            {key: 'createdAt', label: 'Created', tdClass: 'align-middle'},
            {key: 'actions', label: '', thClass: 'w-40'}
          ]"
          :items="degreeChecks"
          borderless
          fixed
          hover
          small
          stacked="md"
          striped
          thead-class="sortable-table-header text-nowrap"
        >
          <template #cell(name)="row">
            <router-link
              :id="`degree-check-${row.index}-link`"
              :disabled="isBusy"
              :to="`degree/${row.item.id}`"
              v-html="`${row.item.name}`"
            />
          </template>
          <template #cell(createdAt)="row">
            {{ row.item.createdAt | moment('MMM D, YYYY') }}
          </template>
          <template #cell(actions)="row">
            <div class="d-flex flex-nowrap">
              <div>
                <b-btn
                  :id="`degree-check-${row.index}-print-btn`"
                  class="p-1"
                  :disabled="isBusy"
                  variant="link"
                  @click.stop="print(row.item.id)"
                >
                  Print
                </b-btn>
              </div>
              <div v-if="$currentUser.canEditDegreeProgress">
                <span class="separator">|</span>
                <b-btn
                  v-if="$currentUser.canEditDegreeProgress"
                  :id="`degree-check-${row.index}-rename-btn`"
                  class="p-1"
                  :disabled="isBusy"
                  variant="link"
                  @click.stop="rename(row.item.id)"
                >
                  Rename
                </b-btn>
              </div>
              <div v-if="$currentUser.canEditDegreeProgress">
                <span class="separator">|</span>
                <b-btn
                  :id="`degree-check-${row.index}-copy-btn`"
                  class="p-1"
                  :disabled="isBusy"
                  variant="link"
                  @click.stop="copy(row.item.id)"
                >
                  Copy
                </b-btn>
              </div>
              <div v-if="$currentUser.canEditDegreeProgress">
                <span class="separator">|</span>
                <b-btn
                  v-if="$currentUser.canEditDegreeProgress"
                  :id="`degree-check-${row.index}-delete-btn`"
                  class="p-1"
                  :disabled="isBusy"
                  variant="link"
                  @click="showDeleteModal(row.item)"
                  @keypress.enter="showDeleteModal(row.item)"
                >
                  Delete
                </b-btn>
              </div>
            </div>
          </template>
        </b-table-lite>
      </div>
    </div>
    <AreYouSureModal
      v-if="templateForDelete"
      :function-cancel="deleteCanceled"
      :function-confirm="deleteConfirmed"
      :modal-body="deleteModalBody"
      :show-modal="!!templateForDelete"
      button-label-confirm="Delete"
      modal-header="Delete Degree"
    />
  </div>
</template>

<script>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import Context from '@/mixins/Context'
import Loading from '@/mixins/Loading'
import Spinner from '@/components/util/Spinner'
import Util from '@/mixins/Util'
import {deleteDegreeTemplate, getDegreeTemplates} from '@/api/degree'

export default {
  name: 'DegreeChecks',
  components: {AreYouSureModal, Spinner},
  mixins: [Context, Loading, Util],
  data: () => ({
    degreeChecks: undefined,
    deleteModalBody: undefined,
    isBusy: false,
    templateForDelete: false
  }),
  mounted() {
    getDegreeTemplates().then(data => {
      this.degreeChecks = data
      this.loaded('Degree Checks loaded')
    })
  },
  methods: {
    deleteCanceled() {
      this.isBusy = false
      this.deleteModalBody = this.templateForDelete = null
      this.$announcer.set('Canceled. Nothing deleted.', 'polite')
    },
    deleteConfirmed() {
      deleteDegreeTemplate(this.templateForDelete.id).then(() => {
        getDegreeTemplates().then(data => {
          this.degreeChecks = data
          this.$announcer.set(`${this.templateForDelete.name} deleted.`, 'polite')
          this.deleteModalBody = this.templateForDelete = null
          this.isBusy = false
        })
      })
    },
    showDeleteModal(template) {
      this.deleteModalBody = `Are you sure you want to delete <b>"${template.name}"</b>?`
      this.$announcer.set('Please confirm delete.', 'polite')
      this.templateForDelete = template
      this.isBusy = true
    }
  }
}
</script>

<style scoped>
.separator {
  color: #ccc;
}
</style>
