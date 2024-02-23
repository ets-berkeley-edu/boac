<template>
  <div id="pagination-widget-outer" role="navigation" aria-label="Pages of list">
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
      @change="onClick"
    >
    </b-pagination>
  </div>
</template>

<script>
export default {
  name: 'Pagination',
  props: {
    clickHandler: {
      required: true,
      type: Function
    },
    initPageNumber: {
      type: Number,
      default: 1
    },
    limit: {
      required: true,
      type: Number
    },
    perPage: {
      required: true,
      type: Number
    },
    size: {
      default: undefined,
      required: false,
      type: String
    },
    totalRows: {
      required: true,
      type: Number
    }
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
