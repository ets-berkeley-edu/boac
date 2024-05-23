<template>
  <div class="d-flex justify-start">
    <span class="sr-only"><span id="total-rows">{{ totalPages }}</span> pages of search results</span>
    <v-pagination
      :id="`pagination-${index}`"
      v-model="currentPage"
      active-color="primary"
      aria-label="Pagination"
      density="comfortable"
      :length="totalPages"
      rounded="md"
      :show-first-last-page="totalPages >= showFirstLastButtonsWhen"
      :total-visible="7"
      variant="flat"
      @next="() => onClick('next')"
      @prev="() => onClick('prev')"
      @update:model-value="v => onClick(v)"
    >
      <template #first="{disabled}">
        <v-btn
          :id="`pagination-${index}-first-page`"
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
          :id="`pagination-${index}-previous-page`"
          aria-label="Previous"
          class="chevron-button rounded-e-0 rounded-s-lg"
          :class="{
            'text-primary': !disabled,
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
      <!--
      <template #item="{isActive, key, page, props}">
        <v-btn
          :id="`pagination-widget-${index}-btn-${key}`"
          class="page-number"
          :class="{'bg-primary border-primary text-white': isActive, 'text-primary': !isActive, 'd-none': hideButton(key)}"
          :text="page"
          tile
          variant="outlined"
          @click="() => console.log(props)"
        />
      </template>
      -->
      <template #next="{disabled}">
        <v-btn
          :id="`pagination-${index}-next-page`"
          class="chevron-button rounded-s-0"
          :class="{
            'text-primary': !disabled,
            'rounded-0': totalPages >= showFirstLastButtonsWhen,
            'rounded-s-0': totalPages < showFirstLastButtonsWhen
          }"
          :disabled="disabled"
          :icon="mdiChevronRight"
          variant="outlined"
          @click="onClick('next')"
        />
      </template>
      <template #last="{disabled}">
        <v-btn
          :id="`pagination-${index}-last-page`"
          class="font-size-14 rounded-e-lg rounded-s-0"
          :class="{'text-primary': !disabled}"
          :disabled="disabled"
          slim
          text="Last"
          variant="outlined"
          @click="onClick(totalPages)"
        />
      </template>
    </v-pagination>
  </div>
</template>

<script setup>
import {computed} from 'vue'
import {mdiChevronLeft, mdiChevronRight} from '@mdi/js'
import {each, toNumber} from 'lodash'

const props = defineProps({
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
})

const showFirstLastButtonsWhen = 11
const currentPage = props.initPageNumber
const totalPages = computed(() =>Math.ceil(props.totalRows / props.perPage))

const intervalId = setInterval(() => {
  const elements = document.querySelectorAll('ul li.v-pagination__item button[ellipsis]')
  if (elements.length) {
    clearInterval(intervalId)
    each(elements, (element, page) => {
      const isEllipsis = element.getAttribute('ellipsis') === 'true'
      element.id = `pagination-${props.index}-page-${isEllipsis ? 'ellipsis' : page}-btn`
      if (isEllipsis) {
        element.setAttribute('style', 'color: #fff !important')
        element.lastElementChild.classList.add('text-grey-darken-2')
      } else if (element.ariaCurrent !== 'true') {
        element.classList.add('text-primary')
      }
      each(['border-1', 'px-5', 'rounded-0'], className => element.classList.add(className))
    })
  }
}, 300)

const onClick = page => {
  if (page === 'prev') {
    props.clickHandler(toNumber(currentPage - 1))
  } else if (page === 'next') {
    props.clickHandler(toNumber(currentPage + 1))
  } else {
    props.clickHandler(toNumber(page))
  }
}
</script>

<style lang="scss">
.chevron-button {
  height: 36px !important;
}
.color-white {
  color: white;
}
.v-pagination {
  ul li {
    margin: 0;
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
