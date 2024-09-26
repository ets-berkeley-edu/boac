<template>
  <div :id="`${idPrefix}-container`" class="d-flex justify-start scroll-margins py-1" tabindex="-1">
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
    >
      <template #first="{disabled}">
        <v-btn
          :id="`${idPrefix}-first`"
          class="font-size-14 px-2"
          color="primary"
          :disabled="disabled"
          slim
          :tabindex="disabled ? -1 : 0"
          tag="a"
          text="First"
          variant="outlined"
          @click="onClick('first')"
          @keyup.enter="onClick('first')"
        />
      </template>
      <template #prev="{disabled}">
        <v-btn
          :id="`${idPrefix}-prev`"
          aria-label="Previous"
          color="primary"
          :disabled="disabled"
          :icon="mdiChevronLeft"
          :tabindex="disabled ? -1 : 0"
          tag="a"
          tile
          variant="outlined"
          @click="onClick('prev')"
          @keyup.enter="onClick('prev')"
        />
      </template>
      <template #item="{isActive, key, page, props: itemProps}">
        <v-btn
          :id="itemProps.ellipsis ? `${idPrefix}-ellipsis` : `${idPrefix}-page-${key}`"
          :aria-current="isActive"
          :aria-label="itemProps.ellipsis ? undefined : `Page ${page}${isActive ? ', current page' : ''}`"
          :class="{
            'bg-surface text-primary': !isActive && !itemProps.ellipsis,
            'bg-primary text-white': isActive && itemProps.ellipsis,
            'pagination-ellipsis': itemProps.ellipsis
          }"
          :tabindex="itemProps.ellipsis ? -1 : 0"
          tag="a"
          :text="page"
          tile
          variant="flat"
          v-bind="props"
          @click="onClick(page)"
          @keyup.enter="onClick(page)"
        />
      </template>
      <template #next="{disabled}">
        <v-btn
          :id="`${idPrefix}-next`"
          color="primary"
          :disabled="disabled"
          :icon="mdiChevronRight"
          :tabindex="disabled ? -1 : 0"
          tag="a"
          variant="outlined"
          @click="onClick('next')"
          @keyup.enter="onClick('next')"
        />
      </template>
      <template #last="{disabled}">
        <v-btn
          :id="`${idPrefix}-last`"
          class="font-size-14 px-2"
          color="primary"
          :disabled="disabled"
          slim
          :tabindex="disabled ? -1 : 0"
          tag="a"
          text="Last"
          variant="outlined"
          @click="onClick('last')"
          @keyup.enter="onClick('last')"
        />
      </template>
    </v-pagination>
  </div>
</template>

<script setup>
import {computed} from 'vue'
import {putFocusNextTick} from '@/lib/utils'
import {toNumber} from 'lodash'
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
  isWidgetAtBottomOfPage: {
    required: false,
    type: Boolean
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

const onClick = page => {
  let nextPage
  let putFocusId
  switch(page) {
  case 'first':
    nextPage = 1
    putFocusId = `${props.idPrefix}-page-1`
    break
  case 'last':
    nextPage = totalPages.value
    putFocusId = `${props.idPrefix}-page-${totalPages.value}`
    break
  case 'prev':
    nextPage = currentPage - 1
    putFocusId = `${props.idPrefix}-page-${currentPage - 1}`
    break
  case 'next':
    nextPage = currentPage + 1
    putFocusId= `${props.idPrefix}-page-${currentPage + 1}`
    break
  default:
    nextPage = page
    putFocusId = `${props.idPrefix}-page-${page}`
  }
  props.clickHandler(toNumber(nextPage)).then(() => {
    if (!props.isWidgetAtBottomOfPage) {
      putFocusNextTick(putFocusId)
    }
  })

}
</script>

<style lang="scss">
.v-pagination {
  ul li {
    margin: 0;
    a {
      border: 1px solid rgb(var(--v-theme-surface-light));
      border-radius: 0 !important;
      height: 36px !important;
      min-width: 40px !important;
      padding: 0 2px;
      width: fit-content !important;
      &:hover {
        text-decoration: none !important;
      }
    }
    &:first-child a {
      border-radius: 4px 0 0 4px !important;
    }
    &:last-child a {
      border-radius: 0 4px 4px 0 !important;
    }
    a.pagination-ellipsis {
      .v-btn__overlay {
        background-color: unset !important;
      }
      .v-btn__content {
        color: rgba(var(--v-theme-on-surface),var(--v-disabled-opacity)) !important;
      }
    }
  }
}
</style>
