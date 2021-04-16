<template>
  <div class="ml-3 mr-3 mt-3">
    <Spinner />
    <div v-if="!loading">
      <b-container>
        <b-row>
          <b-col class="pl-0">
            <b-row>
              Student Information
            </b-row>
          </b-col>
          <b-col>
            <div class="unofficial-label-pill degree-progress-pill">UNOFFICIAL DEGREE PROGRESS REPORT </div>
            <h1 class="print-degree-name pt-2">{{ template.name }}</h1>

            <h4 class="print-page-section-header-sub mb-0">Unit Requirements</h4>
            <div v-if="$_.isEmpty(template.unitRequirements)" class="no-data-text">
              No unit requirements created
            </div>
            <b-table
              id="print-unit-requirements-table"
              :items="template.unitRequirements"
              :fields="fields"
              thead-class="sortable-table-header text-nowrap border-bottom"
              borderless
              responsive
              small
            >
            </b-table>
            <hr class="subsection-divider" />
          </b-col>
        </b-row>
      </b-container>
      <hr class="divider" />
      <hr />
    </div>
  </div>
</template>


<script>
import Context from '@/mixins/Context'
import Loading from '@/mixins/Loading'
import Spinner from '@/components/util/Spinner'
import Util from '@/mixins/Util'
import {getDegreeTemplate} from '@/api/degree'

export default {
  name: 'PrintableDegreeTemplate',
  components: {
    Spinner,
  },
  mixins: [Context, Loading, Util],
  mounted() {
    const id = this.toInt(this.$_.get(this.$route, 'params.id'))

    getDegreeTemplate(id).then(data => {
      this.template = data
      this.loaded(`Printable ${this.template.name} has loaded`)
    })
  },
  data: () => ({
    fields: [
      {
        key: 'name',
        label: 'Type',
        class: 'pl-0'
      },
      {
        key: 'minUnits',
        label: 'Min.',
        class: 'text-right'
      },
      {
        key: 'completedUnits',
        label: 'Completed',
      }
    ],
    template: undefined,
  }),
}
</script>

<style>
.divider {
  background-color: #999;
  border: none;
  color: #999;
  height: 3px;
}
.print-degree-name {
  font-size: 12px;
}
.print-page-section-header-sub {
  font-size: 8px;
}
.unofficial-label-pill {
  background-color: #000000;
  border: 1px solid #000000;
  border-radius: 5px;
  color: #fff;
  font-family: Helvetica;
  font-size: 8px;
  font-weight: bold;
  height: 24px;
  margin-top: 2px;
  padding-top: 6px;
  text-align: center;
  width: auto;
}
.subsection-divider {
  background-color: #999;
  border: none;
  color: #999;
  height: 1px;
}
#print-unit-requirements-table > tbody > tr > td {
  padding: .1rem;
}
#print-unit-requirements-table > thead {
  font-size: 8px;
}
#print-unit-requirements-table {
  font-size: 8px;
}
</style>
