<template>
  <div class="ml-3 mr-3 mt-3">
    <Spinner />
    <div v-if="!loading">
      <b-container fluid>
        <b-row>
          <b-col class="pl-0">
            <b-row>
              Student Information
            </b-row>
          </b-col>
          <b-col />
          <b-col>
            <div class="unofficial-label-pill">UNOFFICIAL DEGREE PROGRESS REPORT </div>
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
      <b-container class="px-0 mx-0" :fluid="true">
        <b-row>
          <b-col
            v-for="position in [1, 2, 3]"
            :key="position"
            class="print-degree-progress-column"
          >
            <template>
              <div>
                <div
                  v-for="category in $_.filter(template.categories, c => c.position === position && $_.isNil(c.parentCategoryId))"
                  :key="category.id"
                >
                  <Category
                    v-if="category.id"
                    :category="category"
                    :position="position"
                    class="print-degree-category"
                  />
                  <div v-if="$_.size(category.courses)" class="pl-1 py-2">
                    <CoursesTable
                      :courses="category.courses"
                      :position="position"
                      class="print-degree-courses"
                    />
                  </div>
                  <div v-if="$_.size(category.subcategories)">
                    <div v-for="subcategory in category.subcategories" :key="subcategory.id">
                      <Category
                        v-if="subcategory.id"
                        :category="subcategory"
                        :position="position"
                        class="print-degree-subcategory"
                      />
                      <div v-if="$_.size(subcategory.courses)" class="pl-1 py-2">
                        <CoursesTable
                          :courses="subcategory.courses"
                          :position="position"
                          class="print-degree-courses"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </template>
          </b-col>
        </b-row>
      </b-container>
    </div>
  </div>
</template>


<script>
import Context from '@/mixins/Context'
import Loading from '@/mixins/Loading'
import Spinner from '@/components/util/Spinner'
import Util from '@/mixins/Util'
import {getDegreeTemplate} from '@/api/degree'
import Category from '@/components/degree/Category.vue'
import CoursesTable from '@/components/degree/CoursesTable.vue'

export default {
  name: 'PrintableDegreeTemplate',
  components: {
    Spinner,
    CoursesTable,
    Category
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

<style scoped>
.degree-progress-category {
  font-size: 12px;
  font-weight: bold;
}
.degree-progress-subcategory {
  font-size: 10px;
  font-weight: bold;
}
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
.print-degree-courses > div > table > tbody > tr > td {
  font-size: 10px;
  padding: 1px;
}
.print-degree-courses > div > table > thead > tr > th {
  font-size: 8px;
}
.subsection-divider {
  background-color: #999;
  border: none;
  color: #999;
  height: 1px;
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
#degree-progress-category-description {
  font-size: 10px;
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
button[id*='-delete-'] {
  display: none;
}
button[id*='-edit-'] {
  display: none;
}
</style>
