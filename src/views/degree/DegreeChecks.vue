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
          responsive
          small
          stacked="md"
          striped
          thead-class="sortable-table-header text-nowrap"
        >
          <template #cell(name)="row">
            <router-link
              :id="`degree-check-${row.index}-link`"
              :to="`degree/${row.item.id}`"
              v-html="`${row.item.name}`"
            ></router-link>
          </template>
          <template #cell(createdAt)="row">
            {{ row.item.createdAt | moment('MMM D, YYYY') }}
          </template>
          <template #cell(actions)="row">
            <div class="d-flex flex-nowrap">
              <b-btn
                :id="`degree-check-${row.index}-print-btn`"
                class="p-1"
                variant="link"
                @click.stop="print(row.item.id)"
              >
                Print
              </b-btn>
              <span class="separator">|</span>
              <b-btn
                v-if="$currentUser.canEditDegreeProgress"
                :id="`degree-check-${row.index}-rename-btn`"
                class="p-1"
                variant="link"
                @click.stop="rename(row.item.id)"
              >
                Rename
              </b-btn>
              <span class="separator">|</span>
              <b-btn
                v-if="$currentUser.canEditDegreeProgress"
                :id="`degree-check-${row.index}-copy-btn`"
                class="p-1"
                variant="link"
                @click.stop="copy(row.item.id)"
              >
                Copy
              </b-btn>
              <span class="separator">|</span>
              <b-btn
                v-if="$currentUser.canEditDegreeProgress"
                :id="`degree-check-${row.index}-delete-btn`"
                class="p-1"
                variant="link"
                @click.stop="del(row.item.id)"
              >
                Delete
              </b-btn>
            </div>
          </template>
        </b-table-lite>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Loading from '@/mixins/Loading'
import Spinner from '@/components/util/Spinner'
import Util from '@/mixins/Util'
import {getDegreeTemplates} from '@/api/degree'

export default {
  name: 'DegreeChecks',
  components: {Spinner},
  mixins: [Context, Loading, Util],
  data: () => ({
    degreeChecks: undefined
  }),
  mounted() {
    getDegreeTemplates().then(data => {
      this.degreeChecks = data
      this.loaded('Degree Checks loaded')
    })
  },
}
</script>

<style scoped>
.separator {
  color: #ccc;
}
</style>
