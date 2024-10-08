<template>
  <div :id="`column-${position}-edit-category`" class="pb-3">
    <div v-if="!existingCategory">
      <div class="font-weight-500">
        Requirement Type (required)
      </div>
      <div>
        <select
          :id="`column-${position}-add-category-select`"
          v-model="selectedCategoryType"
          class="select-menu w-100"
          :disabled="isSaving"
        >
          <option
            :id="`column-${position}-select-option-null`"
            :value="undefined"
          >
            Choose...
          </option>
          <option
            v-for="option in config.degreeCategoryTypeOptions"
            :id="`column-${position}-select-option-${option}`"
            :key="option"
            :disabled="disableCategoryOption(option)"
            :value="option"
          >
            {{ option }}
          </option>
        </select>
      </div>
    </div>
    <div v-if="selectedCategoryType">
      <div v-if="!isCampusRequirements(existingCategory)">
        <label class="font-weight-500" :for="`column-${position}-name-input`">
          {{ selectedCategoryType }} Name (required)
        </label>
        <div>
          <v-text-field
            :id="`column-${position}-name-input`"
            v-model="name"
            :disabled="isSaving"
            hide-details
            maxlength="255"
            @keydown.enter="onSubmit"
          />
          <div class="pl-1">
            <span class="text-surface-variant font-size-12">255 character limit <span v-if="name.length">({{ 255 - name.length }} left)</span></span>
            <span
              v-if="name.length === 255"
              aria-live="polite"
              class="sr-only"
              role="alert"
            >
              Fulfillment requirement name cannot exceed 255 characters.
            </span>
          </div>
        </div>
      </div>
      <div v-if="existingCategory && isCampusRequirements(existingCategory)" class="mt-2">
        <h3 :id="`column-${position}-name`" class="font-weight-bold font-size-18">{{ name }}</h3>
      </div>
      <div v-if="selectedCategoryType === 'Course Requirement'" class="mt-2">
        <UnitsInput
          :disable="isSaving"
          :error-message="unitsErrorMessage"
          :on-submit="onSubmit"
          :range="true"
          :set-units-lower="units => unitsLower = units"
          :set-units-upper="units => unitsUpper = units"
          :units-lower="unitsLower"
          :units-upper="unitsUpper"
        />
      </div>
      <div v-if="selectedCategoryType === 'Course Requirement'" class="mt-2">
        <div class="font-weight-500">
          Transfer Course
        </div>
        <div>
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
      <div v-if="degreeStore.unitRequirements.length && !isCampusRequirements(existingCategory)" class="mt-1">
        <div class="font-weight-500">
          Requirement Fulfillment
        </div>
        <div>
          <SelectUnitFulfillment
            :ref="`column-${position}-unit-requirement-select`"
            :disable="isSaving"
            :initial-unit-requirements="selectedUnitRequirements"
            :on-unit-requirements-change="(value) => selectedUnitRequirements = value"
            :position="position"
          />
        </div>
      </div>
      <div v-if="selectedCategoryType !== 'Course Requirement'" class="mt-2">
        <div class="font-weight-500">
          {{ selectedCategoryType }} Description
        </div>
        <div>
          <v-textarea
            :id="`column-${position}-description-input`"
            v-model="descriptionText"
            density="compact"
            :disabled="isSaving"
            hide-details
            maxlength="255"
            max-rows="6"
            rows="3"
            variant="outlined"
          />
        </div>
      </div>
      <div v-if="!includes(['Category', 'Campus Requirements'], selectedCategoryType)" class="mt-2">
        <div class="font-weight-500 pb-1">
          Requirement Location (required)
        </div>
        <div>
          <select
            :id="`column-${position}-parent-category-select`"
            v-model="selectedParentCategory"
            class="select-menu w-100"
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
              v-for="category in reject(findCategoriesByTypes(['Category', 'Subcategory'], props.position), isCampusRequirements)"
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
    <div class="d-flex justify-end mt-3">
      <div class="mr-2">
        <ProgressButton
          :id="`column-${position}-create-requirement-btn`"
          :action="onSubmit"
          color="primary"
          density="comfortable"
          :disabled="disableSaveButton"
          :in-progress="isSaving"
          :text="isSaving ? 'Saving...' : (existingCategory ? 'Save' : 'Create Requirement')"
        />
      </div>
      <div>
        <v-btn
          :id="`column-${position}-cancel-create-requirement-btn`"
          color="primary"
          density="comfortable"
          :disabled="isSaving"
          text="Cancel"
          variant="outlined"
          @click="cancel"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import ProgressButton from '@/components/util/ProgressButton.vue'
import SelectUnitFulfillment from '@/components/degree/SelectUnitFulfillment'
import UnitsInput from '@/components/degree/UnitsInput'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {clone, differenceBy, each, every, filter, get, includes, isEmpty, map, reject, some} from 'lodash'
import {computed, onMounted, ref, watch} from 'vue'
import {createDegreeCategory, updateCategory} from '@/api/degree'
import {findCategoryById, flattenCategories, getItemsForCoursesTable, isCampusRequirement, validateUnitRange} from '@/lib/degree-progress'
import {refreshDegreeTemplate} from '@/stores/degree-edit-session/utils'
import {useDegreeStore} from '@/stores/degree-edit-session/index'
import {useContextStore} from '@/stores/context'

const props = defineProps({
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
})

const contextStore = useContextStore()
const degreeStore = useDegreeStore()

const config = contextStore.config
const descriptionText = ref(get(props.existingCategory, 'description'))
const isSatisfiedByTransferCourse = ref(get(props.existingCategory, 'isSatisfiedByTransferCourse', false))
const isSaving = ref(false)
const name = ref(get(props.existingCategory, 'name', ''))
const selectedCategoryType = ref(get(props.existingCategory, 'categoryType'))
const selectedParentCategory = ref(undefined)
const selectedUnitRequirements = ref(clone(get(props.existingCategory, 'unitRequirements', [])))
const unitsLower = ref(get(props.existingCategory, 'unitsLower'))
const unitsUpper = ref(get(props.existingCategory, 'unitsUpper'))

watch(selectedCategoryType, option => {
  alertScreenReader(option ? `${selectedCategoryType.value} selected` : 'Unselected')
  if (option) {
    if (selectedCategoryType.value === 'Campus Requirements') {
      name.value = 'Campus Requirements'
      descriptionText.value = 'American History, American Institutions, and American Cultures courses can also count as H/SS courses.'
      putFocusNextTick(`column-${props.position}-description-input`)
    } else {
      descriptionText.value = null
      name.value = ''
      putFocusNextTick(`column-${props.position}-name-input`)
    }
  }
})

onMounted(() => {
  selectedParentCategory.value = props.existingCategory ? findCategoryById(props.existingCategory.parentCategoryId) : null
  putFocusNextTick(props.existingCategory ? `column-${props.position}-name-input` : `column-${props.position}-add-category-select`)
})

const disableSaveButton = computed(() => {
  return isSaving.value
    || !selectedCategoryType.value
    || (!isCampusRequirements(props.existingCategory) && !name.value.trim())
    || (!includes(['Category', 'Campus Requirements'], selectedCategoryType.value) && !selectedParentCategory.value)
    || !!unitsErrorMessage.value
})

const unitsErrorMessage = computed(() => {
  const maxUnitsAllowed = 10
  const validate = selectedCategoryType.value === 'Course Requirement' && (!!unitsLower.value || !!unitsUpper.value)
  const message = validateUnitRange(unitsLower.value, unitsUpper.value, maxUnitsAllowed).message
  return validate ? (message === 'Invalid' ? `Units must be between 1 and ${maxUnitsAllowed}` : message) : null
})

const cancel = () => {
  descriptionText.value = null
  name.value = ''
  selectedCategoryType.value = null
  alertScreenReader('Canceled.')
  props.afterCancel()
}

const disableCategoryOption = option => {
  const hasCampusRequirements = some(findCategoriesByTypes(['Category']), isCampusRequirements)
  const withTypeCategory = reject(findCategoriesByTypes(['Category'], props.position), isCampusRequirements)
  return (option === 'Campus Requirements' && hasCampusRequirements)
    || (!withTypeCategory.length && !includes(['Category', 'Campus Requirements'], option))
}

const disableLocationOption = option => {
  const optionType = option.categoryType
  const selectedType = selectedCategoryType.value
  return (selectedType === 'Subcategory' && optionType === 'Subcategory')
    || (selectedType === 'Subcategory' && optionType === 'Category' && getItemsForCoursesTable(option).length > 0)
    || (selectedType === 'Course Requirement' && optionType === 'Category' && !!option.subcategories.length)
}

const findCategoriesByTypes = (types, position) => {
  const categories = degreeStore.categories
  return filter(flattenCategories(categories), c => (!position || c.position === position) && includes(types, c.categoryType))
}

const isCampusRequirements = category => {
  return selectedCategoryType.value === 'Campus Requirements'
    || (category && !isEmpty(category.courseRequirements) && every(category.courseRequirements, isCampusRequirement))
}

const onChangeParentCategory = option => {
  alertScreenReader(option ? `${selectedParentCategory.value.name} selected` : 'Unselected')
  const existingUnitRequirements = selectedUnitRequirements.value
  const parentUnitRequirements = get(selectedParentCategory.value, 'unitRequirements')

  if (option) {
    const inheritedUnitRequirements = differenceBy(parentUnitRequirements, existingUnitRequirements, 'id')
    each(inheritedUnitRequirements, unitRequirement => {
      this.$refs[`column-${option.position}-unit-requirement-select`].onChangeUnitRequirement(unitRequirement)
    })
    putFocusNextTick(`column-${props.position}-create-requirement-btn`)
  } else {
    each(parentUnitRequirements, unitRequirement => {
      const indexOf = selectedUnitRequirements.value.findIndex(u => u.id === unitRequirement.id)
      selectedUnitRequirements.value.splice(indexOf, 1)
      alertScreenReader(`Removed "${unitRequirement.name}" unit requirement.`)
    })
  }
}

const onSubmit = () => {
  if (!disableSaveButton.value) {
    isSaving.value = true
    const categoryName = name.value
    const parentCategoryId = get(selectedParentCategory.value, 'id')
    const unitRequirementIds = map(selectedUnitRequirements.value, 'id')
    const done = () => {
      alertScreenReader(`${props.existingCategory ? 'Updated' : 'Created'} "${categoryName}" ${selectedCategoryType.value}.`)
      props.afterSave()
      isSaving.value = true
    }
    alertScreenReader('Saving')
    if (props.existingCategory) {
      updateCategory(
        props.existingCategory.id,
        descriptionText.value,
        isSatisfiedByTransferCourse.value,
        name.value,
        parentCategoryId,
        unitRequirementIds,
        unitsLower.value,
        unitsUpper.value
      ).then(() => {
        refreshDegreeTemplate(degreeStore.templateId).then(done)
      })
    } else {
      createDegreeCategory(
        selectedCategoryType.value,
        descriptionText.value,
        isSatisfiedByTransferCourse.value,
        name.value,
        parentCategoryId,
        props.position,
        degreeStore.templateId,
        unitRequirementIds,
        unitsLower.value,
        unitsUpper.value
      ).then(() => {
        refreshDegreeTemplate(degreeStore.templateId).then(done)
      })
    }
  }
}
</script>
