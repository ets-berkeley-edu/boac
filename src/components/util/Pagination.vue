<template>
  <div>
    <span class="sr-only"><span id="total-rows">{{ totalPages }}</span>
      pages of search results</span>
    <b-pagination id="pagination-widget"
                  v-model="currentPage"
                  @input="onClick()"
                  next-text="Next"
                  prev-text="Prev"
                  first-text="First"
                  last-text="Last"
                  :hide-goto-end-buttons="totalPages < 3"
                  label-first-page="Go to first page"
                  label-next-page="Go to next page"
                  label-last-page="Go to last page"
                  label-prev-page="Go to previous page"
                  label-page="Go to page"
                  hide-ellipsis
                  size="md"
                  :total-rows="totalRows"
                  :limit="limit"
                  :per-page="perPage">
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
  created() {
    this.currentPage = this.initPageNumber;
  },
  computed: {
    totalPages() {
      return (this.totalRows / this.perPage) | this.ceil;
    }
  },
  methods: {
    onClick() {
      this.clickHandler(this.currentPage);
    }
  }
};
</script>
