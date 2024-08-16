<template>
  <div v-if="!loading" class="default-margins">
    <div class="border-bottom pb-3">
      <h1 class="overflow-wrap-break-word page-section-header">{{ degreeStore.degreeName || 'Degree Builder' }}</h1>
    </div>
    <div class="border-bottom py-3 w-50">
      <h2 class="sr-only">Requirements</h2>
      <UnitRequirements />
    </div>
    <h2 class="sr-only">Categories</h2>
    <v-container class="mt-2 pa-0" fluid>
      <v-row>
        <v-col
          v-for="position in [1, 2, 3]"
          :id="`degree-template-column-${position}`"
          :key="position"
          class="degree-progress-column"
        >
          <TemplateCategoryColumn :position="position" />
        </v-col>
      </v-row>
    </v-container>
  </div>
  <div v-if="contextStore.config.isVueAppDebugMode">
    <DebugTemplate />
  </div>
</template>

<script setup>
import DebugTemplate from '@/components/degree/DebugTemplate'
import router from '@/router'
import TemplateCategoryColumn from '@/components/degree/TemplateCategoryColumn'
import UnitRequirements from '@/components/degree/UnitRequirements'
import {alertScreenReader, putFocusNextTick, setPageTitle, toInt} from '@/lib/utils'
import {refreshDegreeTemplate} from '@/stores/degree-edit-session/utils'
import {useContextStore} from '@/stores/context'
import {computed, onMounted} from 'vue'
import {useDegreeStore} from '@/stores/degree-edit-session/index'
import {useRoute} from 'vue-router'

const contextStore = useContextStore()
const degreeStore = useDegreeStore()
const loading = computed(() => contextStore.loading)

contextStore.loadingStart()

onMounted(() => {
  const id = toInt(useRoute().params.id)
  refreshDegreeTemplate(id).then(() => {
    if (degreeStore.sid) {
      router.push(`/student/degree/${id}`)
    } else {
      setPageTitle(degreeStore.degreeName)
      contextStore.loadingComplete()
      alertScreenReader(degreeStore.templateId ? `Degree ${degreeStore.degreeName} has loaded` : 'Create degree page has loaded')
      putFocusNextTick('add-unit-requirement')
    }
  })
})
</script>

<style scoped>
.degree-progress-column {
  min-width: 300px;
  padding-bottom: 10px;
}
</style>
