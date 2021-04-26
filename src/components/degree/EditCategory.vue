<template>
  <div :id="`column-${position}-edit-category`" class="border border-1 mb-4 pb-3 pt-2 px-2 rounded">
    <div v-if="!existingCategory" class="ml-1">
      <div class="font-weight-500">
        Requirement Type (required)
      </div>
      <div class="my-2">
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
    <div v-if="selectedCategoryType" class="ml-1">
      <div class="font-weight-500 my-2">
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
        <div class="pl-2">
          <span class="faint-text font-size-12">255 character limit <span v-if="nameInput.length">({{ 255 - nameInput.length }} left)</span></span>
          <span v-if="nameInput.length === 255" class="sr-only" aria-live="polite">
            Fulfillment requirement name cannot exceed 255 characters.
          </span>
        </div>
      </div>
      <div v-if="selectedCategoryType === 'Course Requirement'">
        <div class="font-weight-500 my-2">
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
      <div v-if="selectedCategoryType === 'Course Requirement' && unitRequirements.length">
        <div class="font-weight-500 my-2">
          Requirement Fulfillment
        </div>
        <div class="mb-3">
          <b-select
            :id="`column-${position}-unit-requirement-select`"
            v-model="unitRequirementModel"
            :disabled="isSaving || (unitRequirements.length === selectedUnitRequirements.length)"
            @change="onChangeUnitRequirement"
          >
            <b-select-option :id="`column-${position}-unit-requirement-option-null`" :value="null">Choose...</b-select-option>
            <b-select-option
              v-for="(option, index) in unitRequirements"
              :id="`column-${position}-unit-requirement-option-${index}`"
              :key="index"
              :disabled="$_.includes($_.map(selectedUnitRequirements, 'id'), option.id)"
              :value="option"
            >
              {{ option.name }}
            </b-select-option>
          </b-select>
          <div v-if="selectedUnitRequirements.length">
            <label
              :for="`column-${position}-unit-requirement-list`"
              class="sr-only"
            >
              Selected Requirement Fulfillment(s)
            </label>
            <ul
              :id="`column-${position}-unit-requirement-list`"
              class="pill-list pl-0"
            >
              <li
                v-for="(unitRequirement, index) in selectedUnitRequirements"
                :id="`column-${position}-unit-requirement-${index}`"
                :key="index"
              >
                <div class="align-items-center d-flex justify-content-between mr-3 pill-unit-requirement">
                  <div class="pb-1">
                    {{ unitRequirement.name }}
                  </div>
                  <div>
                    <b-btn
                      :id="`column-${position}-unit-requirement-remove-${index}`"
                      :disabled="isSaving"
                      class="pb-0 px-0 pt-1"
                      variant="link"
                      @click="removeUnitRequirement(unitRequirement)"
                    >
                      <font-awesome icon="times-circle" class="font-size-24 has-error pl-2" />
                      <span class="sr-only">Remove</span>
                    </b-btn>
                  </div>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
      <div v-if="selectedCategoryType !== 'Course Requirement'">
        <div class="font-weight-500 my-2">
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
      <div v-if="selectedCategoryType !== 'Category'" class="my-2">
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
    <div class="d-flex mt-3">
      <div>
        <b-btn
          :id="`column-${position}-create-requirement-btn`"
          class="b-dd-override"
          :disabled="disableSaveButton"
          variant="primary"
          @click="onClickSave"
        >
          <span v-if="isSaving">
            <font-awesome class="mr-1" icon="spinner" spin /> Saving
          </span>
          <span v-if="existingCategory && !isSaving">Update</span>
          <span v-if="!existingCategory && !isSaving">Create Requirement</span>
        </b-btn>
      </div>
      <div>
        <b-btn
          :id="`column-${position}-cancel-create-requirement-btn`"
          :disabled="isSaving"
          variant="link"
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
import Util from '@/mixins/Util'

export default {
  name: 'EditCategory',
  mixins: [DegreeEditSession, Util],
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
    selectedUnitRequirements: [],
    unitRequirementModel: null
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
    onChangeUnitRequirement(option) {
      this.$announcer.polite(option ? `${option.name} selected` : 'Unselected')
      if (option) {
        this.selectedUnitRequirements.push(option)
        this.unitRequirementModel = null
      }
    },
    onClickSave() {
      this.existingCategory ? this.update() : this.create()
    },
    removeUnitRequirement(item) {
      this.$announcer.polite(`${item.name} removed`)
      this.selectedUnitRequirements = this.$_.remove(this.selectedUnitRequirements, selected => selected.id !== item.id)
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
.pill-unit-requirement {
  background-color: #fff;
  border: 1px solid #999;
  border-radius: 5px;
  color: #666;
  margin-top: 8px;
  padding: 4px 12px 4px 12px;
  width: auto;
}
</style>
