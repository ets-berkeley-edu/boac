<template>
  <div>
    <div>
      <label
        for="degree-template-select"
        class="font-weight-700 input-label mt-2 text"
      >Add Degree Check</label>
    </div>
    <b-dropdown
      id="degree-template-select"
      v-model="selectedTemplate"
      class="mb-2 ml-0 transparent"
      block
      :disabled="disabled"
      :lazy="true"
      menu-class="w-100"
      toggle-class="d-flex justify-space-between align-center"
      variant="outline-dark"
    >
      <template #button-content>
        <span v-if="!selectedTemplate">Choose<span class="sr-only">&nbsp;degree check</span>...</span>
        <span v-if="selectedTemplate" class="truncate-with-ellipsis">{{ selectedTemplate.name }}</span>
      </template>
      <b-dropdown-item
        v-for="template in degreeTemplates"
        :id="`degree-template-option-${template.id}`"
        :key="template.id"
        link-class="truncate-with-ellipsis"
        :aria-label="`Add degree check ${template.name}`"
        @click="select(template)"
      >
        {{ template.name }}
      </b-dropdown-item>
    </b-dropdown>
  </div>
</template>

<script>
import {getDegreeTemplates} from '@/api/degree'

export default {
  name: 'DegreeTemplatesMenu',
  props: {
    onSelect: {
      required: true,
      type: Function
    },
    disabled: {
      required: false,
      type: Boolean
    }
  },
  data: () => ({
    degreeTemplates: undefined,
    selectedTemplate: undefined
  }),
  mounted() {
    getDegreeTemplates().then(data => {
      this.degreeTemplates = data
    })
  },
  methods: {
    select(template) {
      this.selectedTemplate = template
      this.onSelect(template)
    }
  }
}
</script>