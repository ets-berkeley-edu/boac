<template>
  <div :id="`${idPrefix}-container`" class="d-flex justify-start" tabindex="-1">
    <span class="sr-only"><span id="total-rows">{{ totalPages }}</span> pages of search results. Use Tab to navigate.</span>
    <v-pagination
      :id="`${idPrefix}-widget`"
      v-model="currentPage"
      active-color="primary"
      aria-label="Pagination"
      density="comfortable"
      :length="totalPages"
      rounded="0"
      :show-first-last-page="totalPages >= showFirstLastButtonsWhen"
      :total-visible="7"
      variant="flat"
      @first="() => onClick('first')"
      @last="() => onClick('last')"
      @next="() => onClick('next')"
      @prev="() => onClick('prev')"
      @update:model-value="v => onClick(v)"
    >
      <template #first="{disabled}">
        <v-btn
          :id="`${idPrefix}-first`"
          class="font-size-14 rounded-e-0 rounded-s-lg"
          color="primary"
          :disabled="disabled"
          slim
          text="First"
          variant="outlined"
          @click="onClick('first')"
        />
      </template>
      <template #prev="{disabled}">
        <v-btn
          :id="`${idPrefix}-prev`"
          aria-label="Previous"
          class="chevron-button"
          color="primary"
          :class="{
            'rounded-0': totalPages >= showFirstLastButtonsWhen,
            'rounded-e-0': totalPages < showFirstLastButtonsWhen
          }"
          :disabled="disabled"
          :icon="mdiChevronLeft"
          tile
          variant="outlined"
          @click="onClick('prev')"
        />
      </template>
      <template #next="{disabled}">
        <v-btn
          :id="`${idPrefix}-next`"
          class="chevron-button rounded-s-0"
          :class="{
            'rounded-0': totalPages >= showFirstLastButtonsWhen,
            'rounded-s-0': totalPages < showFirstLastButtonsWhen
          }"
          color="primary"
          :disabled="disabled"
          :icon="mdiChevronRight"
          variant="outlined"
          @click="onClick('next')"
        />
      </template>
      <template #last="{disabled}">
        <v-btn
          :id="`${idPrefix}-last`"
          class="font-size-14 rounded-s-0 rounded-e-lg"
          color="primary"
          :disabled="disabled"
          slim
          text="Last"
          variant="outlined"
          @click="onClick('last')"
        />
      </template>
    </v-pagination>
  </div>
</template>

<script setup>
import {computed} from 'vue'
import {each, toNumber} from 'lodash'
import {mdiChevronLeft, mdiChevronRight} from '@mdi/js'

const props = defineProps({
  clickHandler: {
    required: true,
    type: Function
  },
  idPrefix: {
    default: 'pagination',
    required: false,
    type: String
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
})

const currentPage = props.initPageNumber
const showFirstLastButtonsWhen = 3
const totalPages = computed(() => Math.ceil(props.totalRows / props.perPage))

const intervalId = setInterval(() => {
  const elements = document.querySelectorAll(`#${props.idPrefix}-widget button[ellipsis]`)
  if (elements.length) {
    clearInterval(intervalId)
    each(elements, element => {
      const isEllipsis = element.getAttribute('ellipsis') === 'true'
      const suffix = isEllipsis ? 'ellipsis' : `page-${(element.ariaLabel || 'unknown').match(/\d+/)[0]}`
      element.id = `${props.idPrefix}-${suffix}`
      if (isEllipsis) {
        element.classList.add('text-surface')
        element.lastElementChild.classList.add('text-medium-emphasis')
      } else if (element.ariaCurrent !== 'true') {
        element.classList.add('text-primary')
      }
      each(['border-1', 'px-5', 'rounded-0'], className => element.classList.add(className))
    })
  }
}, 300)

const onClick = page => {
  switch(page) {
  case 'first':
    props.clickHandler(toNumber(1), 'first')
    break
  case 'last':
    props.clickHandler(toNumber(totalPages.value), 'last')
    break
  case 'prev':
    props.clickHandler(toNumber(currentPage - 1), 'prev')
    break
  case 'next':
    props.clickHandler(toNumber(currentPage + 1), 'next')
    break
  default:
    props.clickHandler(toNumber(page), `page-${page}`)
  }
}
</script>

<style lang="scss">
.chevron-button {
  height: 36px !important;
}
.v-pagination {
  ul li {
    margin: 0;
    button {
      border: 1px solid rgb(var(--v-theme-surface-light));
      height: 40px;
      &.page-number {
        min-width: unset;
        width: 45px !important;
      }
    }
  }
}
</style>
