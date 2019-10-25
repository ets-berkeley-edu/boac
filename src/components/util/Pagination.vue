<template>
  <div>
    <span class="sr-only"><span id="total-rows">{{ totalPages }}</span>
      pages of search results</span>
    <b-pagination
      id="pagination-widget"
      v-model="currentPage"
      :hide-goto-end-buttons="totalPages < 3"
      :total-rows="totalRows"
      :limit="limit"
      :per-page="perPage"
      @change="onClick"
      next-text="Next"
      prev-text="Prev"
      first-text="First"
      last-text="Last"
      hide-ellipsis
      size="md">
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
      return (this.totalRows / this.perPage) | this.ceil;
    }
  },
  created() {
    this.currentPage = this.initPageNumber;
  },
  methods: {
    onClick(page) {
      this.clickHandler(page);
    }
  }
};
</script>
