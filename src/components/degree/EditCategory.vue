<template>
  <div :id="`column-${position}-edit-category`" class="pb-3">
    <div v-if="!existingCategory">
      <div class="font-weight-500">
        Requirement Type (required)
      </div>
      <div class="mb-1 mt-2">
        <b-select
          :id="`column-${position}-add-category-select`"
          v-model="selectedCategoryType"
          :disabled="isSaving"
          @change="onChangeCategorySelect"
        >
          <b-select-option :id="`column-${position}-select-option-null`" :value="null">Choose...</b-select-option>
          <b-select-option
            v-for="option in $config.degreeCategoryTypeOptions"
            :id="`column-${position}-select-option-${option}`"
            :key="option"
            :disabled="(!withTypeCategory.length && option !== 'Category')"
            required
            :value="option"
          >
            {{ option }}
          </b-select-option>
        </b-select>
      </div>
    </div>
    <div v-if="selectedCategoryType" class="mb-1 mt-2">
      <div class="font-weight-500">
        {{ selectedCategoryType }} Name (required)
      </div>
      <div>
        <b-form-input
          :id="`column-${position}-name-input`"
          v-model="nameInput"
          :disabled="isSaving"
          maxlength="255"
          @keypress.enter="create"
        />
        <div class="pl-1">
          <span class="faint-text font-size-12">255 character limit <span v-if="nameInput.length">({{ 255 - nameInput.length }} left)</span></span>
          <span v-if="nameInput.length === 255" class="sr-only" aria-live="polite">
            Fulfillment requirement name cannot exceed 255 characters.
          </span>
        </div>
      </div>
      <div v-if="selectedCategoryType === 'Course Requirement'" class="mb-1 mt-2">
        <div class="font-weight-500">
          Units
        </div>
        <div>
          <b-form-input
            :id="`column-${position}-units-input`"
            v-model="units"
            class="units-input"
            :disabled="isSaving"
            maxlength="3"
            trim
            @keypress.enter="create"
          />
          <span v-if="!isValidUnits" class="has-error faint-text font-size-12">
            Number or numerical range required
          </span>
        </div>
      </div>
      <div v-if="selectedCategoryType === 'Course Requirement' && unitRequirements.length" class="mb-1 mt-2">
        <div class="font-weight-500">
          Requirement Fulfillment
        </div>
        <div class="mb-3">
          <SelectUnitFulfillment
            :disable="isSaving"
            :initial-unit-requirements="selectedUnitRequirements"
            :on-unit-requirements-change="onUnitRequirementsChange"
            :position="position"
          />
        </div>
      </div>
      <div v-if="selectedCategoryType !== 'Course Requirement'" class="mb-1 mt-2">
        <div class="font-weight-500">
          {{ selectedCategoryType }} Description
        </div>
        <div>
          <b-form-textarea
            :id="`column-${position}-description-input`"
            v-model="descriptionText"
            :disabled="isSaving"
            rows="4"
          />
        </div>
      </div>
      <div v-if="selectedCategoryType !== 'Category'" class="mb-1 mt-2">
        <div class="font-weight-500">
          Requirement Location (required)
        </div>
        <div class="my-2">
          <b-select
            :id="`column-${position}-parent-category-select`"
            v-model="selectedParentCategory"
            :disabled="isSaving"
            required
            @change="onChangeParentCategory"
          >
            <b-select-option
              :id="`column-${position}-parent-select-option-null`"
              :value="null"
            >
              Choose...
            </b-select-option>
            <b-select-option
              v-for="category in withTypeCategoryOrSubcategory"
              :id="`column-${position}-parent-select-option-${category.name}`"
              :key="category.id"
              :aria-label="`${category.categoryType} ${category.name}`"
              :disabled="selectedCategoryType === 'Subcategory' && category.categoryType === 'Subcategory'"
              :value="category"
            >
              {{ category.name }}
            </b-select-option>
          </b-select>
        </div>
      </div>
    </div>
    <div class="d-flex mt-2">
      <div class="pr-2">
        <b-btn
          :id="`column-${position}-create-requirement-btn`"
          class="btn-primary-color-override"
          :disabled="disableSaveButton"
          size="sm"
          variant="primary"
          @click="onClickSave"
        >
          <span v-if="isSaving">
            <font-awesome class="mr-1" icon="spinner" spin /> Saving
          </span>
          <span v-if="existingCategory && !isSaving">Save</span>
          <span v-if="!existingCategory && !isSaving">Create Requirement</span>
        </b-btn>
      </div>
      <div>
        <b-btn
          :id="`column-${position}-cancel-create-requirement-btn`"
          class="btn-primary-color-override btn-primary-color-outline-override"
          :disabled="isSaving"
          size="sm"
          variant="outline-primary"
          @click="cancel"
        >
          Cancel
        </b-btn>
      </div>
    </div>
  </div>
</template>

<script>
import DegreeEditSession from '@/mixins/DegreeEditSession'
import SelectUnitFulfillment from '@/components/degree/SelectUnitFulfillment'
import Util from '@/mixins/Util'

export default {
  name: 'EditCategory',
  mixins: [DegreeEditSession, Util],
  components: {SelectUnitFulfillment},
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
  computed: {
    disableSaveButton() {
      return this.isSaving
        || !this.nameInput
        || !this.selectedCategoryType
        || (this.selectedCategoryType !== 'Category' && !this.selectedParentCategory)
        || !this.isValidUnits
    },
    isValidUnits() {
      return this.$_.isEmpty(this.units)
        || /^\d-\d$/.test(this.units)
        || (/^\d+$/.test(this.units) && this.toInt(this.units) > 0)
    },
    withTypeCategory() {
      return this.findCategoriesByTypes(['Category'], this.position)
    },
    withTypeCategoryOrSubcategory() {
      return this.findCategoriesByTypes(['Category', 'Subcategory'], this.position)
    }
  },
  data: () => ({
    units: undefined,
    descriptionText: undefined,
    isSaving: false,
    nameInput: '',
    selectedCategoryType: null,
    selectedParentCategory: null,
    selectedUnitRequirements: []
  }),
  created() {
    if (this.existingCategory) {
      this.units = this.existingCategory.units
      this.descriptionText = this.existingCategory.description
      this.nameInput = this.existingCategory.name
      this.selectedCategoryType = this.existingCategory.categoryType
      this.selectedParentCategory = this.findCategoryById(this.existingCategory.parentCategoryId)
      this.selectedUnitRequirements = this.$_.clone(this.existingCategory.unitRequirements)
    }
    this.putFocusNextTick(`column-${this.position}-add-category-select`)
  },
  methods: {
    cancel() {
      this.descriptionText = null
      this.nameInput = ''
      this.selectedCategoryType = null
      this.afterCancel()
    },
    create() {
      if (!this.disableSaveButton) {
        this.isSaving = true
        this.createCategory({
          categoryType: this.selectedCategoryType,
          description: this.descriptionText,
          name: this.nameInput,
          position: this.position,
          parentCategoryId: this.selectedParentCategory && this.selectedParentCategory.id,
          unitRequirementIds: this.$_.map(this.selectedUnitRequirements, 'id'),
          units: this.units
        }).then(() => {
          this.$announcer.polite(`${this.selectedCategoryType} created`)
          this.afterSave()
        })
      }
    },
    onChangeCategorySelect(option) {
      this.$announcer.polite(option ? `${this.selectedCategoryType} selected` : 'Unselected')
      if (option) {
        this.putFocusNextTick(`column-${this.position}-name-input`)
      }
    },
    onChangeParentCategory(option) {
      this.$announcer.polite(option ? `${this.selectedParentCategory} selected` : 'Unselected')
      if (option) {
        this.putFocusNextTick(`column-${this.position}-create-requirement-btn`)
      }
    },
    onClickSave() {
      this.existingCategory ? this.update() : this.create()
    },
    onUnitRequirementsChange(unitRequirements) {
      this.selectedUnitRequirements = unitRequirements
    },
    update() {
      this.isSaving = true
      this.updateCategory({
        categoryId: this.existingCategory.id,
        description: this.descriptionText,
        name: this.nameInput,
        parentCategoryId: this.selectedParentCategory && this.selectedParentCategory.id,
        unitRequirementIds: this.$_.map(this.selectedUnitRequirements, 'id'),
        units: this.units
      }).then(() => {
        this.$announcer.polite(`${this.selectedCategoryType} created`)
        this.afterSave()
      })
    }
  }
}
</script>

<style scoped>
.units-input {
  max-width: 3.25rem;
}
</style>
