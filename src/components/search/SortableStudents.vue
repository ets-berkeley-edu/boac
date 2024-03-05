<template>
  <v-data-table-virtual
    :id="id"
    v-resize="onResize"
    :cell-props="{class: 'pa-1 pa-md-0 font-size-16'}"
    class="bg-transparent pa-2 pt-md-0"
    :class="{'stacked-table': stackTable}"
    density="compact"
    :headers="headers"
    :items="students"
    :sort-by.sync="sortBy"
    :sort-compare="sortCompare"
    :sort-desc.sync="sortDescending"
    thead-class="sortable-table-header text-nowrap"
  >
    <template #headers="{columns, isSorted, getSortIcon, toggleSort}">
      <tr>
        <template v-for="column in columns" :key="column.key">
          <th class="py-1 px-0">
            <v-btn
              v-if="column.sortable"
              :id="`${id}-sort-by-${column.key}-btn`"
              :append-icon="isSorted(column) ? getSortIcon(column) : undefined"
              class="sortable-table-header text-left px-1"
              density="compact"
              variant="text"
              @click="() => toggleSort(column)"
            >
              {{ column.title }}
            </v-btn>
            <span v-if="!column.sortable" class="sr-only">{{ column.title }}</span>
          </th>
        </template>
      </tr>
    </template>
    <template #item.curated="{item}">
      <div>
        <CuratedStudentCheckbox
          v-if="options.includeCuratedCheckbox"
          :domain="domain"
          :student="item"
        />
      </div>
    </template>
    <template #item.avatar="{item}">
      <div>
        <StudentAvatar
          :key="item.sid"
          size="small"
          :student="item"
        />
        <div v-if="options.includeCuratedCheckbox" class="sr-only">
          <ManageStudent domain="default" :is-button-variant-link="true" :student="item" />
        </div>
      </div>
    </template>
    <template #item.name="{item}">
      <div>
        <span class="sr-only">Student name</span>
        <router-link
          v-if="item.uid"
          :id="`link-to-student-${item.uid}`"
          class="text-primary"
          :class="{'demo-mode-blur': currentUser.inDemoMode}"
          :to="studentRoutePath(item.uid, currentUser.inDemoMode)"
          v-html="lastNameFirst(item)"
        />
        <span
          v-if="!item.uid"
          :id="`student-${item.sid}-has-no-uid`"
          class="font-weight-500"
          :class="{'demo-mode-blur': currentUser.inDemoMode}"
          v-html="lastNameFirst(item)"
        />
        <span
          v-if="item.academicCareerStatus === 'Inactive' || displayAsAscInactive(item) || displayAsCoeInactive(item)"
          class="inactive-info-icon sortable-students-icon"
          uib-tooltip="Inactive"
          aria-label="Inactive"
          tooltip-placement="bottom"
        >
          <v-icon :icon="mdiInformationOutline" />
        </span>
        <span
          v-if="item.academicCareerStatus === 'Completed'"
          class="sortable-students-icon"
          uib-tooltip="Graduated"
          aria-label="Graduated"
          tooltip-placement="bottom"
        >
          <v-icon :icon="mdiSchool" />
        </span>
      </div>
    </template>
    <template #item.sid="{item}">
      <div>
        <span class="sr-only">S I D </span>
        <span :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ item.sid }}</span>
      </div>
    </template>
    <template v-if="!options.compact" #item.major="{item}">
      <div>
        <span class="sr-only">Major</span>
        <div v-if="!item.majors || item.majors.length === 0">--<span class="sr-only">No data</span></div>
        <div
          v-for="major in item.majors"
          :key="major"
        >
          {{ major }}
        </div>
      </div>
    </template>
    <template v-if="!options.compact" #item.expectedGraduationTerm="{item}">
      <div>
        <span class="sr-only">Expected graduation term</span>
        <div v-if="!item.expectedGraduationTerm">--<span class="sr-only">No data</span></div>
        <span class="text-nowrap">{{ abbreviateTermName(item.expectedGraduationTerm && item.expectedGraduationTerm.name) }}</span>
      </div>
    </template>
    <template v-if="!options.compact" #item.enrolledUnits="{item}">
      <div>
        <span class="sr-only">Term units</span>
        <div>{{ _get(item.term, 'enrolledUnits', 0) }}</div>
      </div>
    </template>
    <template v-if="!options.compact" #item.cumulativeUnits="{item}">
      <div>
        <span class="sr-only">Units completed</span>
        <div v-if="!item.cumulativeUnits">--<span class="sr-only">No data</span></div>
        <div v-if="item.cumulativeUnits">{{ numFormat(item.cumulativeUnits, '0.00') }}</div>
      </div>
    </template>
    <template v-if="!options.compact" #item.cumulativeGPA="{item}">
      <div>
        <span class="sr-only">GPA</span>
        <div v-if="_isNil(item.cumulativeGPA)">--<span class="sr-only">No data</span></div>
        <div v-if="!_isNil(item.cumulativeGPA)">{{ round(item.cumulativeGPA, 3) }}</div>
      </div>
    </template>
    <template #item.alertCount="{item}">
      <div>
        <span class="sr-only">Issue count</span>
        <div class="pr-2">
          <PillAlert
            v-if="!item.alertCount"
            :aria-label="`No alerts for ${item.name}`"
            color="gray"
            outlined
          >
            0
          </PillAlert>
          <PillAlert
            v-if="item.alertCount"
            :aria-label="`${item.alertCount} alerts for ${item.name}`"
            color="warn"
            outlined
          >
            {{ item.alertCount }}
          </PillAlert>
        </div>
      </div>
    </template>
  </v-data-table-virtual>
</template>

<script>
import Context from '@/mixins/Context'
import CuratedStudentCheckbox from '@/components/curated/dropdown/CuratedStudentCheckbox'
import ManageStudent from '@/components/curated/dropdown/ManageStudent'
import PillAlert from '@/components/util/PillAlert'
import StudentAvatar from '@/components/student/StudentAvatar'
import Util from '@/mixins/Util'
import {displayAsAscInactive, displayAsCoeInactive} from '@/berkeley'
import {sortComparator} from '@/lib/utils'

export default {
  name: 'SortableStudents',
  components: {
    CuratedStudentCheckbox,
    ManageStudent,
    PillAlert,
    StudentAvatar
  },
  mixins: [Context, Util],
  props: {
    domain: {
      required: true,
      type: String
    },
    id: {
      default: 'sortable-group-students',
      required: false,
      type: String
    },
    options: {
      type: Object,
      default: () => ({
        compact: false,
        includeCuratedCheckbox: false,
        reverse: false,
        sortBy: 'lastName'
      })
    },
    students: {
      required: true,
      type: Array
    }
  },
  data: () => ({
    headers: undefined,
    sortBy: undefined,
    sortDescending: undefined,
    stackTable: false
  }),
  computed: {
    headerProps() {
      return {
        class: this.$vuetify.display.mdAndDown ? 'd-none' : ''
      }
    }
  },
  watch: {
    sortBy() {
      this.onChangeSortBy()
    },
    sortDescending() {
      this.onChangeSortBy()
    }
  },
  mounted() {
    this.onResize()
  },
  created() {
    this.sortBy = this.options.sortBy
    this.sortDescending = this.options.reverse

    const sortable = this.students.length > 1
    this.headers = []
    if (this.options.includeCuratedCheckbox) {
      this.headers = this.headers.concat(this.createHeader({key: 'curated', value: 'curated', title: ''}))
    }
    this.headers = this.headers.concat([
      this.createHeader({key: 'avatar', title: 'Photo', value: 'photo', clazz: 'pr-0', visuallyHidden: true}),
      this.createHeader({key: 'name', title: 'Name', value: 'lastName'}),
      this.createHeader({key: 'sid', title: 'SID', value: 'sid'})
    ])
    if (this.options.compact) {
      this.headers = this.headers.concat([
        this.createHeader({key: 'alertCount', title: 'Alerts', value: 'alertCount', clazz: 'alert-count', align: 'end'})
      ])
    } else {
      this.headers = this.headers.concat([
        this.createHeader({key: 'major', title: 'Major', value: 'majors[0]', sortable: sortable, clazz: 'truncate-with-ellipsis'}),
        this.createHeader({key: 'expectedGraduationTerm', title: 'Grad', value: 'expectedGraduationTerm.id', sortable: sortable}),
        this.createHeader({key: 'enrolledUnits', title: 'Term units', value: 'term.enrolledUnits', sortable: sortable}),
        this.createHeader({key: 'cumulativeUnits', title: 'Units completed', value: 'cumulativeUnits', sortable: sortable}),
        this.createHeader({key: 'cumulativeGPA', title: 'GPA', value: 'cumulativeGPA', sortable: sortable}),
        this.createHeader({key: 'alertCount', title: 'Alerts', value: 'alertCount', sortable: sortable, clazz: 'alert-count', align: 'end'})
      ])
    }
  },
  methods: {
    abbreviateTermName: termName =>
      termName &&
      termName
        .replace('20', ' \'')
        .replace('Spring', 'Spr')
        .replace('Summer', 'Sum'),
    displayAsAscInactive,
    displayAsCoeInactive,
    normalizeForSort(value) {
      return this._isString(value) ? value.toLowerCase() : value
    },
    createHeader({key, title, value, sortable=false, clazz=null, align=null, visuallyHidden=false}) {
      let header = {
        cellProps: visuallyHidden ? {} : {'data-label': title},
        key: key,
        title: title,
        value: value
      }
      if (sortable) {
        header['sortable'] = sortable
      }
      if (clazz) {
        header['class'] = clazz
      }
      if (align) {
        header['align'] = align
      }
      return header
    },
    onChangeSortBy() {
      const field = this._find(this.headers, ['value', this._get(this.sortBy, 0)])
      this.alertScreenReader(`Sorted by ${field.title}${this.sortDescending ? ', descending' : ''}`)
    },
    onResize() {
      this.stackTable = this.$vuetify.display.mdAndDown
    },
    sortCompare(a, b, sortBy, sortDesc) {
      let aValue = this._get(a, sortBy)
      let bValue = this._get(b, sortBy)
      // If column type is number then nil is treated as zero.
      aValue = this._isNil(aValue) && this._isNumber(bValue) ? 0 : this.normalizeForSort(aValue)
      bValue = this._isNil(bValue) && this._isNumber(aValue) ? 0 : this.normalizeForSort(bValue)
      let result = sortComparator(aValue, bValue)
      if (result === 0) {
        this._each(['lastName', 'firstName', 'sid'], field => {
          result = sortComparator(
            this.normalizeForSort(this._get(a, field)),
            this.normalizeForSort(this._get(b, field))
          )
          // Secondary sort is always ascending
          result *= sortDesc ? -1 : 1
          // Break from loop if comparator result is non-zero
          return result === 0
        })
      }
      return result
    }
  }
}
</script>

<style>
th.alert-count {
  padding-right: 15px;
}
.sortable-students-icon {
  margin-left: 5px;
}
</style>
