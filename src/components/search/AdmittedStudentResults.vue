<template>
  <div>
    <h2 id="admit-results-page-header" class="font-size-18">
      {{ pluralize('admitted student', results.totalAdmitCount) }}<span v-if="searchPhrase">  matching '{{ searchPhrase }}'</span>
    </h2>
    <div class="mb-2 ml-1">
      <AdmitDataWarning :updated-at="_get(results.admits, '[0].updatedAt')" />
    </div>
    <div v-if="_size(results.admits) < results.totalAdmitCount" class="mb-2">
      Showing the first {{ _size(results.admits) }} admitted students.
    </div>
    <CuratedGroupSelector
      context-description="Search"
      domain="admitted_students"
      :students="results.admits"
    />
    <div>
      <SortableAdmits :admitted-students="results.admits" />
    </div>
  </div>
</template>

<script>
import AdmitDataWarning from '@/components/admit/AdmitDataWarning'
import CuratedGroupSelector from '@/components/curated/dropdown/CuratedGroupSelector'
import SortableAdmits from '@/components/admit/SortableAdmits'
import Util from '@/mixins/Util'

export default {
  name: 'AdmittedStudentResults',
  mixins: [Util],
  components: {
    AdmitDataWarning,
    CuratedGroupSelector,
    SortableAdmits,
  },
  props: {
    results: {
      required: true,
      type: Object
    },
    searchPhrase: {
      required: true,
      type: String,
      validator: v => typeof v === 'string' || [null, undefined].includes(v)
    }
  }
}
</script>
