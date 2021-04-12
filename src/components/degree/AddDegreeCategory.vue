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
      <div v-if="selectedCategoryType === 'Course'">
        <div class="font-weight-500 my-2">
          Requirement Fulfillment
        </div>
        <div>
          <b-select
            :id="`column-${position}-requirement-fulfillment-select`"
            :disabled="isSaving"
            @change="onChangeRequirementFulfillment"
          >
            <b-select-option :id="`column-${position}-requirement-fulfillment-option-null`" :value="null">Choose...</b-select-option>
            <b-select-option
              v-for="option in requirementFulfillmentOptions"
              :id="`column-${position}-requirement-fulfillment-option-${option}`"
              :key="option"
              :value="option"
            >
              {{ option }}
            </b-select-option>
          </b-select>
          <div v-if="selectedRequirementFulfillments.length">
            <label :for="`column-${position}-requirement-fulfillment-list`" class="sr-only">Selected Requirement Fulfillment(s)</label>
            <ul
              :id="`column-${position}-requirement-fulfillment-list`"
              class="pill-list pl-0"
            >
              <li
                v-for="(fulfillment, index) in selectedRequirementFulfillments"
                :id="`column-${position}-requirement-fulfillment-${index}`"
                :key="index"
              >
                <span class="pill pill-attachment text-uppercase text-nowrap">
                  {{ fulfillment }}
                  <b-btn
                    :id="`column-${position}-requirement-fulfillment-remove-${index}`"
                    :disabled="isSaving"
                    class="px-0 pt-1"
                    variant="link"
                    @click.prevent="removeRequirementFulfillment(fulfillment)"
                  >
                    <font-awesome icon="times-circle" class="font-size-24 has-error pl-2" />
                    <span class="sr-only">Remove</span>
                  </b-btn>
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>
      <div v-if="selectedCategoryType !== 'Course'">
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
            <b-select-option :id="`column-${position}-parent-select-option-null`" :value="null">Choose...</b-select-option>
            <b-select-option
              v-for="category in withTypeCategory"
              :id="`column-${position}-parent-select-option-${category.name}`"
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
  computed: {
    withTypeCategory() {
      return this.findCategoriesByType('Category', this.position)
    }
  },
  data: () => ({
    courseUnits: undefined,
    descriptionText: undefined,
    isSaving: false,
    nameInput: undefined,
    requirementFulfillmentOptions: [
      'Larry',
      'Curly',
      'Moe'
    ],
    selectedCategoryType: null,
    selectedParentCategory: null,
    selectedRequirementFulfillments: []
  }),
  created() {
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
    onChangeRequirementFulfillment(option) {
      this.$announcer.polite(option ? `${option} selected` : 'Unselected')
      if (option) {
        this.selectedRequirementFulfillments.push(option)
      }
    },
    removeRequirementFulfillment(item) {
      this.$announcer.polite(`${item} removed`)
      this.selectedRequirementFulfillments = this.$_.remove(this.selectedRequirementFulfillments, f => f !== item)
    }
  }
}
</script>
