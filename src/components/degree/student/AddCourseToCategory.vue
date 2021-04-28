<template>
  <div>
    <div v-if="isMenuOpen">
      <div class="font-weight-500 font-size-18">
        Add Courses
      </div>
      <div class="my-2">
        <b-select
          :id="`column-${position}-category-${category.id}-add-course-select`"
          v-model="selected"
          :disabled="isSaving"
          @change="onChangeSelect"
        >
          <b-select-option id="degree-check-select-option-null" :value="null">Choose...</b-select-option>
          <b-select-option
            v-for="course in courses"
            :id="`degree-check-select-option-${course.id}`"
            :key="course.id"
            required
            :value="course"
          >
            {{ course.name }}
          </b-select-option>
        </b-select>
      </div>

      <div class="d-flex mt-3">
        <div>
          <b-btn
            id="save-degree-check-btn"
            class="b-dd-override"
            :disabled="!selected"
            variant="primary"
            @click="onClickSave"
          >
            <span v-if="isSaving">
              <font-awesome class="mr-1" icon="spinner" spin /> Saving
            </span>
            <span v-if="!isSaving">Save Degree Check</span>
          </b-btn>
        </div>
        <div>
          <b-btn
            id="cancel-create-degree-check-btn"
            :disabled="isSaving"
            variant="link"
            @click="cancel"
          >
            Cancel
          </b-btn>
        </div>
      </div>
    </div>
    <div v-if="!isMenuOpen">
      <b-btn
        v-if="$currentUser.canEditDegreeProgress"
        :id="`column-${position}-add-course-to-category-${category.id}`"
        class="align-items-center d-flex flex-row-reverse p-0"
        :disabled="disableButtons"
        variant="link"
        @click.prevent="openMenu"
      >
        <div class="font-size-14 text-nowrap">
          Add Course
        </div>
        <div class="font-size-14 pr-1">
          <font-awesome icon="plus" />
        </div>
      </b-btn>
    </div>
  </div>
</template>

<script>
import DegreeEditSession from '@/mixins/DegreeEditSession'
import Util from '@/mixins/Util'

export default {
  name: 'AddCourseToCategory',
  mixins: [DegreeEditSession, Util],
  props: {
    category: {
      required: true,
      type: Object
    },
    position: {
      required: true,
      type: Number
    },
    student: {
      default: undefined,
      required: false,
      type: Object
    }
  },
  data: () => ({
    courses: [
      {
        id: 1,
        name: 'Fee'
      },
      {
        id: 2,
        name: 'Fi'
      },
      {
        id: 3,
        name: 'Fo'
      },
      {
        id: 4,
        name: 'Fum'
      }
    ],
    isMenuOpen: false,
    isSaving: false,
    selected: null
  }),
  methods: {
    cancel() {
      this.isMenuOpen = this.isSaving =false
      this.selected = null
      this.setDisableButtons(false)
      this.$announcer.polite('Cancelled')
    },
    onChangeSelect(option) {
      console.log(`onChangeSelect: ${option}`)
    },
    onClickSave() {
      this.isMenuOpen = this.isSaving = false
      this.selected = null
      this.setDisableButtons(false)
      this.$announcer.polite('TODO: describe what happened')
    },
    openMenu() {
      this.setDisableButtons(true)
      this.isMenuOpen = true
      this.$announcer.polite('The \'Add Course\' menu is open.')
      this.putFocusNextTick(`column-${this.position}-category-${this.category.id}-add-course-select`)
    }
  }
}
</script>
