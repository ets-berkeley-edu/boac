<template>
  <div :id="`pagination-widget-${index}-outer`" class="d-flex justify-start">
    <span class="sr-only"><span id="total-rows">{{ totalPages }}</span>
      pages of search results</span>
    <v-pagination
      :id="`pagination-widget-${index}`"
      v-model="currentPage"
      aria-label="Pagination"
      density="compact"
      :show-first-last-page="totalPages >= 3"
      :length="totalPages"
      :total-visible="totalVisible"
      variant="outlined"
    >
      <template #first="{disabled}">
        <v-btn
          :id="`pagination-widget-${index}-btn-first`"
          class="font-size-14 rounded-e-0"
          :class="{'text-primary': !disabled}"
          :disabled="disabled"
          slim
          variant="outlined"
          @click="onClick(1)"
        >
          First
        </v-btn>
      </template>
      <template #prev="{disabled}">
        <v-btn
          :id="`pagination-widget-${index}-btn-prev`"
          class="font-size-14 rounded-0"
          :class="{'text-primary': !disabled}"
          :disabled="disabled"
          slim
          variant="outlined"
          @click="onClick('prev')"
        >
          Prev
        </v-btn>
      </template>
      <template #item="{isActive, key, page}">
        <v-btn
          :id="`pagination-widget-${index}-btn-${key}`"
          :aria-hidden="hideButton(key)"
          class="page-number font-size-14 px-0"
          :class="{'bg-primary border-primary text-white': isActive, 'text-primary': !isActive, 'd-none': hideButton(key)}"
          slim
          tile
          variant="outlined"
          @click="onClick(page)"
        >
          {{ page }}
        </v-btn>
      </template>
      <template #next="{disabled}">
        <v-btn
          :id="`pagination-widget-${index}-btn-next`"
          class="font-size-14 rounded-0"
          :class="{'text-primary': !disabled}"
          :disabled="disabled"
          slim
          variant="outlined"
          @click="onClick('next')"
        >
          Next
        </v-btn>
      </template>
      <template #last="{disabled}">
        <v-btn
          :id="`pagination-widget-${index}-btn-last`"
          class="font-size-14 rounded-s-0"
          :class="{'text-primary': !disabled}"
          :disabled="disabled"
          slim
          variant="outlined"
          @click="onClick(totalPages)"
        >
          Last
        </v-btn>
      </template>
    </v-pagination>
  </div>
</template>

<script setup>
import {startsWith, toNumber} from 'lodash'
</script>

<script>
export default {
  name: 'Pagination',
  props: {
    clickHandler: {
      required: true,
      type: Function
    },
    index: {
      type: Number,
      default: 0
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
    },
    totalVisible() {
      // Account for extra buttons that will be suppressed. For the first n pages, only the ellipsis button needs to be hidden.
      if (this.currentPage <= (this.limit + 2) / 2) {
        return this.limit + 1
      } else {
        return this.limit + 3
      }
    }
  },
  created() {
    this.currentPage = this.initPageNumber
  },
  methods: {
    hideButton(key) {
      // Suppress extra buttons to hide ellipsis and prevent gaps between page numbers.
      const midpoint = Math.ceil(this.totalVisible / 2)
      if (startsWith(key, 'ellipsis')) {
        return true
      } else if (this.currentPage <= midpoint) {
        return key < (this.currentPage - midpoint) || key > (this.limit)
      } else if (this.currentPage >= this.totalPages - midpoint) {
        return key <= (this.totalPages - this.limit)
      } else {
        return key <= (this.currentPage - midpoint) || key >= (this.currentPage + midpoint)
      }
    },
    onClick(page) {
      if (page === 'prev') {
        this.clickHandler(toNumber(this.currentPage - 1))
      } else if (page === 'next') {
        this.clickHandler(toNumber(this.currentPage + 1))
      } else {
        this.clickHandler(toNumber(page))
      }
    }
  }
}
</script>

<style lang="scss">
.v-pagination {
  ul li {
    margin: 0px;
    button {
      border: 1px solid rgb(var(--v-theme-faint));
      height: 40px;
      &.page-number {
        min-width: unset;
        width: 45px !important;
      }
    }
  }
}
</style>
