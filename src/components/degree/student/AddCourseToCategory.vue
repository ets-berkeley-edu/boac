<template>
  <div>
    <div v-if="isMenuOpen">
      <div class="font-weight-500 font-size-18">
        Add Courses
      </div>
      <div class="my-2">
        <b-select
          id="add-course-select"
          v-model="selected"
          :disabled="isSaving"
          :lazy="true"
          no-caret
          :toggle-text="`Assign a course to category ${parentCategory.name}`"
        >
          <b-select-option
            id="add-course-select-option-null"
            :value="null"
            @click="onSelect(null)"
          >
            Choose...
          </b-select-option>
          <b-form-select-option-group
            v-for="(options, label) in optionGroups"
            :key="label"
            :label="label"
          >
            <template v-if="options.length">
              <b-form-select-option
                v-for="option in options"
                :id="`add-course-select-option-${option.id}`"
                :key="option.id"
                :value="option"
                @click="onSelect(option)"
              >
                {{ option.name }}
              </b-form-select-option>
            </template>
            <template v-if="!options.length">
              <b-form-select-option :disabled="true" :value="undefined">
                -- None --
              </b-form-select-option>
            </template>
          </b-form-select-option-group>
        </b-select>
      </div>
      <div class="d-flex mt-3">
        <div>
          <b-btn
            id="add-course-save-btn"
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
            id="add-course-cancel-btn"
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
        :id="`column-${position}-add-course-to-category-${parentCategory.id}`"
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
    parentCategory: {
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
    isMenuOpen: false,
    isSaving: false,
    optionGroups: undefined,
    selected: null
  }),
  watch: {
    isMenuOpen(value) {
      if (value) {
        this.optionGroups = {
          'Unassigned': this.$_.cloneDeep(this.unassignedCourses),
          'Assigned': [{id: 1, name: 'Fee'}, {id: 2, name: 'Fi'}, {id: 3, name: 'Fo'}, {id: 4, name: 'Fum'}]
        }
      }
    }
  },
  methods: {
    cancel() {
      this.isMenuOpen = this.isSaving =false
      this.setDisableButtons(false)
      this.$announcer.polite('Cancelled')
    },
    onClickSave() {
      this.isSaving = true
      this.createCategory({
        categoryType: 'Course Requirement',
        description: null,
        name: this.selected.name,
        parentCategoryId: this.parentCategory.id,
        position: this.position,
        skipRefresh: true,
        unitRequirementIds: [],
        units: this.selected.units
      }).then(category => {
        this.assignCourseToCategory({course: this.selected, category}).then(() => {
          this.isMenuOpen = this.isSaving = false
          this.selected = null
          this.setDisableButtons(false)
          this.$announcer.polite(`Course added to ${this.parentCategory.name}`)
        })
      })
    },
    onSelect(option) {
      this.$announcer.polite(option ? `${option.name} selected` : 'Selection set to null.')
    },
    openMenu() {
      this.setDisableButtons(true)
      this.isMenuOpen = true
      this.$announcer.polite('The \'Add Course\' menu is open.')
      this.putFocusNextTick(`column-${this.position}-category-${this.parentCategory.id}-add-course-select`)
    }
  }
}
</script>
