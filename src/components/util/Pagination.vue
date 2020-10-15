<template>
  <div id="pagination-widget-outer" role="navigation" aria-label="pagination">
    <span class="sr-only"><span id="total-rows">{{ totalPages }}</span>
      pages of search results</span>
    <b-pagination
      id="pagination-widget"
      v-model="currentPage"
      :hide-goto-end-buttons="totalPages < 3"
      :total-rows="totalRows"
      :limit="limit"
      :per-page="perPage"
      next-text="Next"
      prev-text="Prev"
      first-text="First"
      last-text="Last"
      hide-ellipsis
      size="md"
      @change="onClick">
    </b-pagination>
  </div>
</template>

<script>
export default {
  name: 'Pagination',
  props: {
    clickHandler: Function,
    initPageNumber: {
      type: Number,
      default: 1
    },
    limit: Number,
    perPage: Number,
    size: String,
    totalRows: Number
  },
  data: () => ({
    currentPage: undefined
  }),
  computed: {
    totalPages() {
      return Math.ceil(this.totalRows / this.perPage)
    }
  },
  created() {
    this.currentPage = this.initPageNumber
  },
  methods: {
    onClick(page) {
      this.clickHandler(page)
    }
  }
}
</script>
