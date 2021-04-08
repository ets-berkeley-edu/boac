<template>
  <b-container class="px-0 mx-0">
    <b-row>
      <b-col
        v-for="columnNumber in [1, 2, 3]"
        :key="columnNumber"
        class="degree-progress-column"
      >
        <div class="d-flex flex-row pb-3">
          <div class="pill degree-progress-pill px-2">{{ `Column ${columnNumber}` }}</div>
          <b-btn
            :id="`unit-requirement-col-${columnNumber}-create-link`"
            class="d-flex flex-row-reverse justify-content-end text-nowrap py-0"
            variant="link"
          >
            {{ `Add column ${columnNumber} requirement` }}
            <font-awesome icon="plus" class="m-1" />
          </b-btn>
        </div>
        <div v-if="$_.isEmpty(requirementCategoriesByColumn[columnNumber])" class="no-data-text pb-3">
          {{ `No column ${columnNumber} requirements` }}
        </div>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
export default {
  name: 'RequirementCategories',
  computed: {
    requirementCategoriesByColumn() {
      return this.$_.groupBy(this.requirementCategories, 'columnNumber')
    }
  }
}
</script>
