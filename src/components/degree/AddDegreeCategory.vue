<template>
  <div>
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
        <b-select-option :value="null">Choose...</b-select-option>
        <b-select-option
          v-for="option in withTypeCategory.length ? $config.degreeCategoryTypeOptions : this.$_.filter($config.degreeCategoryTypeOptions, o => o !== 'Subcategory')"
          :key="option"
          :value="option"
        >
          {{ option }}
        </b-select-option>
      </b-select>
    </div>
    <div v-if="selectedCategoryType">
      <div class="font-weight-500 my-2">
        {{ selectedCategoryType }} Name (required)
      </div>
      <div>
        <b-form-input
          :id="`column-${position}-name-input`"
          v-model="nameInput"
          :disabled="isSaving"
          maxlength="255"
          @keypress.enter="() => nameInput && create()"
        />
      </div>
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
      <div v-if="selectedCategoryType === 'Subcategory'">
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
            <b-select-option :value="null">Choose...</b-select-option>
            <b-select-option
              v-for="category in withTypeCategory"
              :key="category.id"
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
          :disabled="isSaving || !nameInput || !selectedCategoryType || (selectedCategoryType === 'Subcategory' && !selectedParentCategory)"
          variant="primary"
          @click="create"
        >
          <span v-if="isSaving">
            <font-awesome class="mr-1" icon="spinner" spin /> Saving
          </span>
          <span v-if="!isSaving">Create Requirement</span>
        </b-btn>
      </div>
      <div>
        <b-btn
          :id="`column-${position}-cancel-create-requirement-btn`"
          :disabled="isSaving"
          variant="link"
          @click="cancelCreateRequirement"
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
  name: 'AddDegreeCategory',
  mixins: [DegreeEditSession, Util],
  props: {
    afterCancel: {
      required: true,
      type: Function
    },
    afterCreate: {
      required: true,
      type: Function
    },
    position: {
      required: true,
      type: Number
    }
  },
  data: () => ({
    courseUnits: undefined,
    descriptionText: undefined,
    isSaving: false,
    nameInput: undefined,
    selectedCategoryType: null,
    selectedParentCategory: null,
    withTypeCategory: undefined
  }),
  created() {
    this.withTypeCategory = this.$_.filter(this.categories, c => {
      return c.position === this.position && c.categoryType === 'Category'
    })
    this.putFocusNextTick(`column-${this.position}-add-category-select`)
  },
  methods: {
    cancelCreateRequirement() {
      this.descriptionText = null
      this.nameInput = null
      this.selectedCategoryType = null
      this.afterCancel()
    },
    create() {
      this.isSaving = true
      this.createCategory({
        categoryType: this.selectedCategoryType,
        courseUnits: this.courseUnits,
        description: this.descriptionText,
        name: this.nameInput,
        position: this.position,
        parentCategoryId: this.selectedParentCategory && this.selectedParentCategory.id
      }).then(category => {
        this.$announcer.polite(`${category.categoryType} created`)
        this.afterCreate()
        this.setDisableButtons(false)
      })
    },
    onChangeCategorySelect() {
      this.$announcer.polite(`${this.selectedCategoryType} selected`)
      this.putFocusNextTick(`column-${this.position}-name-input`)
    },
    onChangeParentCategory() {
      this.$announcer.polite(`${this.selectedParentCategory} selected`)
      this.putFocusNextTick(`column-${this.position}-create-requirement-btn`)
    }
  }
}
</script>
