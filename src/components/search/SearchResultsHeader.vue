<template>
  <div>
    <div class="align-items-center d-flex">
      <div class="mr-2">
        <h1 class="page-section-header">Search Results</h1>
      </div>
      <div v-if="!loading && (queryText || author || fromDate || toDate || postedBy !== 'anyone' || student || topic)" class="pb-1">
        [<b-btn
          id="edit-search-btn"
          class="px-0"
          variant="link"
          @click.prevent="openAdvancedSearch"
        >
          edit search
        </b-btn>]
      </div>
    </div>
    <div v-if="!loading">
      <div class="font-weight-500 py-2" v-html="description" />
      <div v-if="!hasSearchResults" id="page-header-no-results">
        <div>Suggestions:</div>
        <ul>
          <li>Keep your search term simple.</li>
          <li>Check your spelling and try again.</li>
          <li>Search classes by section title, e.g., <strong>AMERSTD 10</strong>.</li>
          <li>Avoid using generic terms, such as <strong>test</strong> or <strong>enrollment</strong>.</li>
          <li>Longer search terms may refine results; <strong>registration fees</strong> instead of <strong>registration</strong>.</li>
          <li>Abbreviations of section titles may not return results; <strong>COMPSCI 161</strong> instead of <strong>CS 161</strong>.</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import Loading from '@/mixins/Loading'
import SearchSession from '@/mixins/SearchSession'
import Util from '@/mixins/Util'

export default {
  name: 'SearchResultsHeader',
  mixins: [Loading, SearchSession, Util],
  props: {
    results: {
      required: true,
      type: Object
    }
  },
  computed: {
    description() {
      const phrases = []
      let total = 0
      const push = (noun, count, included) => {
        if (included) {
          total += count
          const phrase = this.pluralize(noun, count, {'0': '<i>zero</i>', '1': 'one'})
          phrases.push(count ? `<a href="#${noun}-results-page-header">${phrase}</a>` : phrase)
        }
      }
      push('admit', this.results.totalAdmitCount, this.includeStudents)
      push('student', this.results.totalStudentCount, this.includeStudents)
      push('course', this.results.totalCourseCount, this.includeStudents)
      push('note', this.$_.size(this.results.notes), this.includeStudents)
      push('appointment', this.$_.size(this.results.appointments), this.includeStudents)
      return total ? `Results include ${this.oxfordJoin(phrases)}` : 'No matching records found.'
    },
    hasSearchResults() {
      return this.results.totalStudentCount
        || this.results.totalCourseCount
        || this.results.totalAdmitCount
        || this.$_.size(this.results.notes)
        || this.$_.size(this.results.appointments)
    }
  },
  methods: {
    openAdvancedSearch() {
      this.showAdvancedSearch = true
      this.$announcer.polite('Advanced search is open')
    }
  }
}
</script>
