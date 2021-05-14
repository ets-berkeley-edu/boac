<template>
  <div>
    <div>
      <label
        for="degree-template-select"
        class="font-size-14 font-weight-bolder input-label text mt-2"
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
      toggle-class="d-flex justify-content-between align-items-center"
      variant="outline-dark"
    >
      <template #button-content>
        <span v-if="!selectedTemplate">Choose...</span>
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
      this.onSelect(template.degree_name, template.id)
    }
  }
}
</script>