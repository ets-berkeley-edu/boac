<template>
  <div>
    <div v-if="isMenuOpen">
      <div class="font-size-14 font-weight-500 pt-2">
        Duplicate Course
      </div>
      <div class="my-2">
        <b-select
          id="add-course-select"
          v-model="selected"
          :disabled="isSaving || !options.length"
          :lazy="true"
          no-caret
        >
          <b-select-option
            id="add-course-select-option-null"
            :value="null"
            @click="onSelect"
          >
            Choose...
          </b-select-option>
          <b-form-select-option
            v-for="option in options"
            :id="`add-course-select-option-${option.id}`"
            :key="option.id"
            :value="option"
            @click="onSelect"
          >
            {{ option.name }}
          </b-form-select-option>
        </b-select>
      </div>
      <div class="d-flex mt-3">
        <div>
          <b-btn
            id="add-course-save-btn"
            class="btn-primary-color-override"
            :disabled="isSaving || !selected"
            variant="primary"
            @click="onClickSave"
          >
            <span v-if="isSaving">
              <font-awesome class="mr-1" icon="spinner" spin /> Saving
            </span>
            <span v-if="!isSaving">Save</span>
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
      <span v-if="!options.length" aria-live="polite" class="sr-only">No courses available to copy.</span>
      <b-btn
        v-if="currentUser.canEditDegreeProgress"
        id="duplicate-existing-course"
        class="align-items-center d-flex flex-row-reverse p-0"
        :disabled="disableButtons || !options.length"
        variant="link"
        @click.prevent="openMenu"
      >
        <div class="font-size-16 text-nowrap">
          Duplicate Course
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
  name: 'DuplicateExistingCourse',
  mixins: [DegreeEditSession, Util],
  data: () => ({
    isMenuOpen: false,
    isSaving: false,
    selected: null
  }),
  computed: {
    options() {
      const courses = this.courses.assigned.concat(this.courses.unassigned)
      return this._filter(this._sortBy(courses, [c => c.name.toLowerCase()], ['name', 'id']), c => !c.isCopy)
    }
  },
  methods: {
    cancel() {
      this.isMenuOpen = this.isSaving = false
      this.setDisableButtons(false)
      this.$announcer.polite('Canceled')
      this.putFocusNextTick('duplicate-existing-course')
    },
    onClickSave() {
      this.isSaving = true
      this.$announcer.polite('Saving')
      this.copyCourse(this.selected.id).then(course => {
        this.isMenuOpen = this.isSaving = false
        this.selected = null
        this.setDisableButtons(false)
        this.$announcer.polite('Course duplicated and put in the list of Unassigned.')
        this.putFocusNextTick(`assign-course-${course.id}-menu-container`, 'button')
      })
    },
    onSelect() {
      this.$announcer.polite(this.selected ? `${this.selected.name} selected` : 'Selection set to null.')
    },
    openMenu() {
      this.setDisableButtons(true)
      this.isMenuOpen = true
      this.$announcer.polite('The \'Duplicate Course\' menu is open.')
      this.putFocusNextTick('add-course-select')
    }
  }
}
</script>
