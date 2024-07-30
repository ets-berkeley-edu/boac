<template>
  <div :id="`column-${position}-edit-category`">
    <div v-if="!existingCategory">
      <div class="font-weight-500">
        Requirement Type (required)
      </div>
      <div>
        <select
          :id="`column-${position}-add-category-select`"
          v-model="selectedCategoryType"
          class="select-menu"
          :disabled="isSaving"
        >
          <option
            :id="`column-${position}-select-option-null`"
            :value="null"
            @select="onChangeCategorySelect"
          >
            Choose...
          </option>
          <option
            v-for="option in config.degreeCategoryTypeOptions"
            :id="`column-${position}-select-option-${option}`"
            :key="option"
            :disabled="disableCategoryOption(option)"
            :value="option"
            @select="onChangeCategorySelect"
          >
            {{ option }}
          </option>
        </select>
      </div>
    </div>
    <div v-if="selectedCategoryType" class="mt-3">
      <div v-if="!isCampusRequirements(existingCategory)">
        <div class="font-weight-500">
          {{ selectedCategoryType }} Name (required)
        </div>
        <div>
          <v-text-field
            :id="`column-${position}-name-input`"
            v-model="name"
            density="compact"
            :disabled="isSaving"
            hide-details
            maxlength="255"
            variant="outlined"
            @keydown.enter="onSubmit"
          />
          <div class="pl-1">
            <span class="text-grey font-size-12">255 character limit <span v-if="name.length">({{ 255 - name.length }} left)</span></span>
            <span v-if="name.length === 255" class="sr-only" aria-live="polite">
              Fulfillment requirement name cannot exceed 255 characters.
            </span>
          </div>
        </div>
      </div>
      <div v-if="existingCategory && isCampusRequirements(existingCategory)" class="mt-3">
        <h3 :id="`column-${position}-name`" class="font-weight-bold font-size-18">{{ name }}</h3>
      </div>
      <div v-if="selectedCategoryType === 'Course Requirement'">
        <UnitsInput
          :disable="isSaving"
          :error-message="unitsErrorMessage"
          :on-submit="onSubmit"
          :range="true"
          :set-units-lower="setUnitsLower"
          :set-units-upper="setUnitsUpper"
          :units-lower="unitsLower"
          :units-upper="unitsUpper"
        />
      </div>
      <div v-if="selectedCategoryType === 'Course Requirement'">
        <div class="font-weight-500 pb-1">
          Transfer Course
        </div>
        <div class="mb-3">
          <v-checkbox
            id="is-satisfied-by-transfer-course-checkbox"
            v-model="isSatisfiedByTransferCourse"
            color="primary"
            density="compact"
            hide-details
            label="Mark transfer course as purple"
          />
        </div>
      </div>
      <div v-if="unitRequirements.length && !isCampusRequirements(existingCategory)" class="mt-3">
        <div class="font-weight-500">
          Requirement Fulfillment
        </div>
        <div>
          <SelectUnitFulfillment
            :ref="`column-${position}-unit-requirement-select`"
            :disable="isSaving"
            :initial-unit-requirements="selectedUnitRequirements"
            :on-unit-requirements-change="onUnitRequirementsChange"
            :position="position"
          />
        </div>
      </div>
      <div v-if="selectedCategoryType !== 'Course Requirement'" class="mt-3">
        <div class="font-weight-500">
          {{ selectedCategoryType }} Description
        </div>
        <div>
          <v-textarea
            :id="`column-${position}-description-input`"
            v-model="descriptionText"
            :disabled="isSaving"
            hide-details
            max-rows="10"
            rows="4"
            variant="outlined"
          />
        </div>
      </div>
      <div v-if="!_includes(['Category', 'Campus Requirements'], selectedCategoryType)" class="mt-3">
        <div class="font-weight-500 pb-1">
          Requirement Location (required)
        </div>
        <div>
          <select
            :id="`column-${position}-parent-category-select`"
            v-model="selectedParentCategory"
            class="select-menu"
            :disabled="isSaving"
            required
          >
            <option
              :id="`column-${position}-parent-select-option-null`"
              :value="null"
              @select="onChangeParentCategory"
            >
              Choose...
            </option>
            <option
              v-for="category in withTypeCategoryOrSubcategory"
              :id="`column-${position}-parent-select-option-${category.name}`"
              :key="category.id"
              :aria-label="`${category.categoryType} ${category.name}`"
              :disabled="disableLocationOption(category)"
              :value="category"
              @select="onChangeParentCategory"
            >
              {{ category.name }}
            </option>
          </select>
        </div>
      </div>
    </div>
    <div class="d-flex mt-4">
      <div class="mr-1">
        <ProgressButton
          :id="`column-${position}-create-requirement-btn`"
          :action="onSubmit"
          color="primary"
          :disabled="disableSaveButton"
          :in-progress="isSaving"
          :text="isSaving ? 'Saving...' : (existingCategory ? 'Save' : 'Create Requirement')"
        />
      </div>
      <div>
        <v-btn
          :id="`column-${position}-cancel-create-requirement-btn`"
          color="primary"
          :disabled="isSaving"
          variant="text"
          @click="cancel"
        >
          Cancel
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import SelectUnitFulfillment from '@/components/degree/SelectUnitFulfillment'
import UnitsInput from '@/components/degree/UnitsInput'
import Util from '@/mixins/Util'
import {alertScreenReader} from '@/lib/utils'
import {createDegreeCategory, updateCategory} from '@/api/degree'
import {
  findCategoriesByTypes,
  findCategoryById,
  getItemsForCoursesTable,
  isCampusRequirement,
  validateUnitRange
} from '@/lib/degree-progress'
import {refreshDegreeTemplate} from '@/stores/degree-edit-session/utils'
import ProgressButton from '@/components/util/ProgressButton.vue'

export default {
  name: 'EditCategory',
  components: {ProgressButton, UnitsInput, SelectUnitFulfillment},
  mixins: [Context, DegreeEditSession, Util],
  props: {
    afterCancel: {
      required: true,
      type: Function
    },
    afterSave: {
      required: true,
      type: Function
    },
    existingCategory: {
      default: undefined,
      required: false,
      type: Object
    },
    position: {
      required: true,
      type: Number
    }
  },
  data: () => ({
    descriptionText: undefined,
    isSatisfiedByTransferCourse: undefined,
    isSaving: false,
    name: '',
    selectedCategoryType: null,
    selectedParentCategory: null,
    selectedUnitRequirements: [],
    unitsLower: undefined,
    unitsUpper: undefined
  }),
  computed: {
    disableSaveButton() {
      return this.isSaving
        || !this.selectedCategoryType
        || (!this.isCampusRequirements(this.existingCategory) && !this.name.trim())
        || (!this._includes(['Category', 'Campus Requirements'], this.selectedCategoryType) && !this.selectedParentCategory)
        || !!this.unitsErrorMessage
    },
    hasCampusRequirements() {
      return this._some(findCategoriesByTypes(['Category']), this.isCampusRequirements)
    },
    unitsErrorMessage() {
      const validate = this.selectedCategoryType === 'Course Requirement' && (!!this.unitsLower || !!this.unitsUpper)
      return validate ? validateUnitRange(this.unitsLower, this.unitsUpper, 10).message : null
    },
    withTypeCategory() {
      return this._reject(findCategoriesByTypes(['Category'], this.position), this.isCampusRequirements)
    },
    withTypeCategoryOrSubcategory() {
      return this._reject(findCategoriesByTypes(['Category', 'Subcategory'], this.position), this.isCampusRequirements)
    }
  },
  created() {
    if (this.existingCategory) {
      this.descriptionText = this.existingCategory.description
      this.isSatisfiedByTransferCourse = this.existingCategory.isSatisfiedByTransferCourse
      this.name = this.existingCategory.name
      this.selectedCategoryType = this.existingCategory.categoryType
      this.selectedParentCategory = findCategoryById(this.existingCategory.parentCategoryId)
      this.selectedUnitRequirements = this._clone(this.existingCategory.unitRequirements)
      this.unitsLower = this.existingCategory.unitsLower
      this.unitsUpper = this.existingCategory.unitsUpper
      this.putFocusNextTick(`column-${this.position}-name-input`)
    } else {
      this.putFocusNextTick(`column-${this.position}-add-category-select`)
    }
  },
  methods: {
    cancel() {
      this.descriptionText = null
      this.name = ''
      this.selectedCategoryType = null
      this.afterCancel()
    },
    disableCategoryOption(option) {
      return (option === 'Campus Requirements' && this.hasCampusRequirements)
        || (!this.withTypeCategory.length && !this._includes(['Category', 'Campus Requirements'], option))
    },
    disableLocationOption(option) {
      const optionType = option.categoryType
      const selectedType = this.selectedCategoryType
      return (selectedType === 'Subcategory' && optionType === 'Subcategory')
        || (selectedType === 'Subcategory' && optionType === 'Category' && getItemsForCoursesTable(option).length > 0)
        || (selectedType === 'Course Requirement' && optionType === 'Category' && !!option.subcategories.length)
    },
    isCampusRequirements(category) {
      return this.selectedCategoryType === 'Campus Requirements'
        || (category && !this._isEmpty(category.courseRequirements) && this._every(category.courseRequirements, isCampusRequirement))
    },
    onChangeCategorySelect(option) {
      alertScreenReader(option ? `${this.selectedCategoryType} selected` : 'Unselected')
      if (option) {
        if (this.selectedCategoryType === 'Campus Requirements') {
          this.name = 'Campus Requirements'
          this.descriptionText = 'American History, American Institutions, and American Cultures courses can also count as H/SS courses.'
          this.putFocusNextTick(`column-${this.position}-description-input`)
        } else {
          this.descriptionText = null
          this.name = ''
          this.putFocusNextTick(`column-${this.position}-name-input`)
        }
      }
    },
    onChangeParentCategory(option) {
      alertScreenReader(option ? `${this.selectedParentCategory.name} selected` : 'Unselected')
      const existingUnitRequirements = this.selectedUnitRequirements
      const parentUnitRequirements = this._get(this.selectedParentCategory, 'unitRequirements')

      if (option) {
        const inheritedUnitRequirements = this._differenceBy(parentUnitRequirements, existingUnitRequirements, 'id')
        this._each(inheritedUnitRequirements, unitRequirement => {
          this.$refs[`column-${option.position}-unit-requirement-select`].onChangeUnitRequirement(unitRequirement)
        })
        this.putFocusNextTick(`column-${this.position}-create-requirement-btn`)
      } else {
        this._each(parentUnitRequirements, unitRequirement => this.removeUnitRequirement(unitRequirement))
      }
    },
    onSubmit() {
      if (!this.disableSaveButton) {
        this.isSaving = true
        const parentCategoryId = this.selectedParentCategory && this.selectedParentCategory.id
        const unitRequirementIds = this._map(this.selectedUnitRequirements, 'id')
        const done = () => {
          alertScreenReader(`${this.selectedCategoryType} ${this.existingCategory ? 'updated' : 'created'}`)
          this.afterSave()
        }
        if (this.existingCategory) {
          updateCategory(
            this.existingCategory.id,
            this.descriptionText,
            this.isSatisfiedByTransferCourse,
            this.name,
            parentCategoryId,
            unitRequirementIds,
            this.unitsLower,
            this.unitsUpper
          ).then(() => {
            refreshDegreeTemplate(this.templateId).then(done)
          })
        } else {
          createDegreeCategory(
            this.selectedCategoryType,
            this.descriptionText,
            this.isSatisfiedByTransferCourse,
            this.name,
            parentCategoryId,
            this.position,
            this.templateId,
            unitRequirementIds,
            this.unitsLower,
            this.unitsUpper
          ).then(() => {
            refreshDegreeTemplate(this.templateId).then(done)
          })
        }
      }
    },
    onUnitRequirementsChange(unitRequirements) {
      this.selectedUnitRequirements = unitRequirements
    },
    setUnitsLower(units) {
      this.unitsLower = units
    },
    setUnitsUpper(units) {
      this.unitsUpper = units
    }
  }
}
</script>
