<template>
  <div>
    <div v-if="$_.isEmpty(courses)" class="no-data-text">
      No courses
    </div>
    <b-table
      id="unit-requirements-table"
      borderless
      class="mb-2 mt-0"
      :fields="fields"
      :items="courses"
      small
      stacked="sm"
      thead-class="sortable-table-header text-nowrap border-bottom"
    >
      <template #cell(courseUnits)="row">
        <span class="font-size-14">{{ $_.isNil(row.item.courseUnits) ? '&mdash;' : row.item.courseUnits }}</span>
      </template>
      <template #cell(unitRequirements)="row">
        <span v-if="row.item.unitRequirements.length" class="font-size-14">
          {{ oxfordJoin($_.map(row.item.unitRequirements, 'name')) }}
        </span>
      </template>
      <template v-if="$currentUser.canEditDegreeProgress" #cell(actions)="row">
        <div class="d-flex justify-content-end">
          <b-btn
            :id="`column-${position}-edit-category-${row.item.id}-btn`"
            class="font-size-14 pl-1 pr-0 py-0"
            :disabled="disableButtons"
            variant="link"
            @click="edit(row.item)"
          >
            <font-awesome icon="edit" />
            <span class="sr-only">Edit {{ row.item.name }}</span>
          </b-btn>
          <b-btn
            :id="`column-${position}-delete-course-${row.item.id}-btn`"
            class="font-size-14 pl-1 pr-0 py-0"
            :disabled="disableButtons"
            variant="link"
            @click="deleteCourse(row.item)"
          >
            <font-awesome icon="trash-alt" />
            <span class="sr-only">Delete {{ row.item.name }}</span>
          </b-btn>
        </div>
      </template>
    </b-table>
    <AreYouSureModal
      v-if="courseForDelete"
      :function-cancel="deleteCanceled"
      :function-confirm="deleteConfirmed"
      :modal-body="`Are you sure you want to delete <strong>&quot;${courseForDelete.name}&quot;</strong>`"
      :show-modal="!!courseForDelete"
      button-label-confirm="Delete"
      modal-header="Delete Course"
    />
  </div>
</template>

<script>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import Util from '@/mixins/Util'

export default {
  name: 'DegreeTemplateCoursesTable',
  mixins: [DegreeEditSession, Util],
  components: {AreYouSureModal},
  props: {
    courses: {
      required: true,
      type: Array
    },
    position: {
      required: true,
      type: Number
    }
  },
  data: () => ({
    courseForDelete: undefined,
    courseForEdit: undefined,
    fields: [
      {
        key: 'name',
        label: 'Course',
        class: 'font-size-12 pl-0'
      },
      {
        key: 'courseUnits',
        label: 'Units',
        class: 'font-size-12 pr-2 text-right'
      },
      {
        key: 'unitRequirements',
        label: 'Fulfillment',
        class: 'font-size-12'
      },
      {
        key: 'actions',
        label: '',
        class: 'd-flex flex-row font-size-12 justify-content-end pr-0'
      }
    ]
  }),
  methods: {
    deleteCanceled() {
      this.putFocusNextTick(`column-${this.position}-delete-course-${this.courseForDelete.id}-btn`)
      this.courseForDelete = null
      this.$announcer.polite('Canceled. Nothing deleted.')
      this.setDisableButtons(false)
    },
    deleteConfirmed() {
      this.deleteCategory(this.courseForDelete.id).then(() => {
        this.$announcer.polite(`${this.courseForDelete.name} deleted.`)
        this.courseForDelete = null
        this.setDisableButtons(false)
        this.putFocusNextTick('page-header')
      })
    },
    deleteCourse(course) {
      this.setDisableButtons(true)
      this.courseForDelete = course
      this.$announcer.polite(`Delete ${course.name}`)
    },
    edit(course) {
      this.$announcer.polite(`Edit ${course.name}`)
      // TODO: putFocusNextTick on input
    }
  }
}
</script>
