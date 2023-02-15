<template>
  <div>
    <h2 id="admit-results-page-header" class="font-size-18">
      {{ pluralize('admitted student', results.totalAdmitCount) }}<span v-if="queryText">  matching '{{ queryText }}'</span>
    </h2>
    <div class="mb-2 ml-1">
      <AdmitDataWarning :updated-at="$_.get(results.admits, '[0].updatedAt')" />
    </div>
    <div v-if="$_.size(results.admits) < results.totalAdmitCount" class="mb-2">
      Showing the first {{ $_.size(results.admits) }} admitted students.
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
import SearchSession from '@/mixins/SearchSession'
import SortableAdmits from '@/components/admit/SortableAdmits'
import Util from '@/mixins/Util'

export default {
  name: 'AdmittedStudentResults',
  mixins: [SearchSession, Util],
  components: {
    AdmitDataWarning,
    CuratedGroupSelector,
    SortableAdmits,
  },
  props: {
    results: {
      required: true,
      type: Object
    }
  }
}
</script>
