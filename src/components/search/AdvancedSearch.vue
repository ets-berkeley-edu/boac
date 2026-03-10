<template>
  <div class="align-center d-flex w-100 justify-center" role="search">
    <div class="d-flex w-66 w-sm-50">
      <label id="basic-search-input-label" class="sr-only">basic search</label>
      <AccessibleCombobox
        :key="searchStore.autocompleteInputResetKey"
        :aria-description="`${labelForSearchInput()}`"
        class="d-flex on-surface mr-1 mr-sm-2 flex-grow-1"
        :clazz="{
          'basic-search ml-auto': true,
          'search-focus-in': shouldExpandInput,
          'search-focus-out': !shouldExpandInput
        }"
        clearable
        :disabled="searchStore.isSearching"
        :get-value="() => queryTextModel"
        id-prefix="basic-search"
        input-type="search"
        :is-busy="searchStore.isSearching"
        :items="searchStore.searchHistory"
        label="Search"
        list-label="Previous Searches"
        :menu-props="{'location': 'bottom'}"
        :on-submit="search"
        :on-update-focused="isFocused => searchStore.setIsFocusOnSearch(isFocused)"
        open-on-focus
        placeholder="/ to search"
        :when-item-selected="search"
        :set-value="v => queryTextModel = v"
      />
    </div>
    <div class="d-flex w-33 w-sm-50">
      <v-btn
        id="go-search"
        class="btn-search ml-sm-1 mr-2 mr-sm-3"
        :disabled="isSearchDisabled"
        :icon="$vuetify.display.width < mobileBreakpoint ? mdiMagnify : false"
        :text="$vuetify.display.width >= mobileBreakpoint ? 'Search' : undefined"
        variant="outlined"
        @keydown.enter="search"
        @click.stop="search"
      />
      <AdvancedSearchModal v-if="(currentUser.canAccessAdvisingData || currentUser.canAccessCanvasData) && !isPeerAdvisor(currentUser)" />
    </div>
  </div>
</template>

<script setup>
import {computed, onMounted, onUnmounted} from 'vue'
import {get, isEmpty, trim} from 'lodash'
import {mdiMagnify} from '@mdi/js'
import {useDisplay} from 'vuetify'
import {useRoute, useRouter} from 'vue-router'
import AccessibleCombobox from '@/components/util/AccessibleCombobox'
import AdvancedSearchModal from '@/components/search/AdvancedSearchModal'
import {addToSearchHistory, getMySearchHistory} from '@/api/search'
import {labelForSearchInput} from '@/lib/search'
import {putFocusNextTick} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {useDegreeStore} from '@/stores/degree-edit-session/index'
import {useSearchStore} from '@/stores/search'
import {isPeerAdvisor} from '@/lib/boa-user.js'

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const display = useDisplay()
const isSearchDisabled = computed(() => {
  const q = trim(searchStore.queryText)
  return searchStore.isSearching || isEmpty(q) || q === route.query.q
})
const mobileBreakpoint = 650
const queryTextModel = computed({
  get: () => searchStore.queryText || null,
  set: v => searchStore.setQueryText(v)
})
const route = useRoute()
const router = useRouter()
const searchStore = useSearchStore()
const shouldExpandInput = computed(() => display.width.value >= mobileBreakpoint && (searchStore.isFocusOnSearch || searchStore.queryText))

onMounted(() => {
  document.addEventListener('keyup', onKeyUp, true)
  searchStore.resetAdvancedSearch(route.query.q)
  getMySearchHistory().then(history => searchStore.setSearchHistory(history))
})

onUnmounted(() => {
  document.removeEventListener('keyup', onKeyUp)
})

const onKeyUp = event => {
  // Disable hot-key when, for example, user is editing a degree-progress note.
  const disableHotKey = useDegreeStore().disableButtons
  if (!disableHotKey && event.keyCode === 191) {
    // forward slash key
    const el = get(event, 'currentTarget.activeElement')
    const ignore = ['textbox'].includes(get(el, 'role')) || ['INPUT'].includes(get(el, 'tagName'))
    if (!ignore) {
      putFocusNextTick('basic-search-input')
    }
  }
}

const search = () => {
  if (!isSearchDisabled.value) {
    const q = trim(searchStore.queryText)
    if (q) {
      const searchPage = isPeerAdvisor(currentUser) ? {
        path: '/peer_advisor/search',
        query: {
          q: q
        }
      } : {
        path: '/search',
        query: {
          admits: currentUser.canAccessAdmittedStudents,
          courses: currentUser.canAccessCanvasData,
          notes: currentUser.canAccessAdvisingData,
          students: true,
          q
        }
      }
      searchStore.setIsSearching(true)
      router.push(searchPage)
      addToSearchHistory(q).then(history => {
        searchStore.setSearchHistory(history)
      })
    } else {
      putFocusNextTick('basic-search-input')
    }
  }
}
</script>

<style scoped>
:deep(.search-focus-in) {
  border: 0;
  flex: 1 0 100%;
  max-width: 300px;
  transition: max-width ease-out 0.2s;
}
:deep(.search-focus-out) {
  max-width: 200px;
  transition: min-width ease-in 0.2s;
}
.btn-search {
  background-color: transparent;
  color: rgb(var(--v-theme-surface));
  font-size: 16px;
  height: 46px;
  letter-spacing: 1px;
  padding: 6px 8px;
}
.btn-search:hover {
  background-color: rgb(var(--v-theme-surface));
  border-color: rgb(var(--v-theme-surface));
  color: rgb(var(--v-theme-primary));
}
</style>
