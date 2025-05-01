<template>
  <div class="default-margins">
    <div v-if="successMessage" class="mb-3 mr-3 mt-6">
      <v-alert
        id="alert-batch-created"
        aria-live="polite"
        class="font-weight-bold"
        closable
        color="info"
        density="compact"
        fade
        role="status"
        variant="tonal"
      >
        <span class="font-weight-bold">Success!</span> {{ successMessage }}
      </v-alert>
    </div>
    <h1 id="page-header" class="mb-2">
      Degree Checks
    </h1>
    <div v-if="currentUser.canEditDegreeProgress" class="align-center d-flex font-weight-medium mb-3">
      <v-btn
        id="degree-check-create-btn"
        class="font-size-16 letter-spacing-normal px-0 text-no-wrap"
        color="primary"
        density="comfortable"
        to="/degree/new"
        variant="text"
      >
        <div class="align-center d-flex">
          <v-icon color="primary" :icon="mdiPlus" />
          <div>
            Create new degree check
          </div>
        </div>
      </v-btn>
      <div v-if="size(degreeTemplates)" class="mx-2">|</div>
      <v-btn
        v-if="size(degreeTemplates)"
        id="degree-check-batch-btn"
        class="font-size-16 letter-spacing-normal px-0 text-no-wrap"
        color="primary"
        density="comfortable"
        text="Batch degree checks"
        to="/degree/batch"
        variant="text"
      />
    </div>
    <div v-if="!contextStore.loading">
      <div v-if="degreeTemplates.length">
        <div v-if="unarchivedDegreeTemplates.length">
          <DegreeTemplatesDataTable
            :degree-templates="unarchivedDegreeTemplates"
            mode="unarchived"
            :on-update-degree-template="onUpdateDegreeTemplate"
          />
        </div>
        <div v-if="!unarchivedDegreeTemplates.length">
          There are no degree templates available.
        </div>
        <div class="mt-6">
          <v-btn
            id="show-hide-archived-degree-templates"
            :aria-expanded="isShowingArchivedTemplates"
            :aria-label="`${isShowingArchivedTemplates ? 'Hide' : 'Show'} `"
            class="font-weight-bold show-hide-archived-btn text-no-wrap"
            color="primary"
            variant="text"
            @click="() => isShowingArchivedTemplates = !isShowingArchivedTemplates"
          >
            <v-icon :icon="isShowingArchivedTemplates ? mdiMenuDown : mdiMenuRight" size="24" />
            {{ isShowingArchivedTemplates ? 'Hide' : 'Show' }} archived degree checks ({{ archivedDegreeTemplates.length }})
          </v-btn>
          <v-expand-transition>
            <DegreeTemplatesDataTable
              v-if="isShowingArchivedTemplates"
              :degree-templates="archivedDegreeTemplates"
              mode="archived"
              :on-update-degree-template="onUpdateDegreeTemplate"
            />
          </v-expand-transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {filter as _filter, size, sortBy} from 'lodash'
import {computed, onMounted, ref} from 'vue'
import {mdiMenuDown, mdiMenuRight, mdiPlus} from '@mdi/js'
import {useRoute} from 'vue-router'
import {getDegreeTemplates} from '@/api/degree'
import {useContextStore} from '@/stores/context'
import DegreeTemplatesDataTable from '@/components/degree/DegreeTemplatesDataTable'

const contextStore = useContextStore()

const archivedDegreeTemplates = computed(() => _filter(degreeTemplates.value, 'archivedAt'))
const currentUser = contextStore.currentUser
const degreeTemplates = ref([])
const isShowingArchivedTemplates = ref(false)
const successMessage = ref(useRoute().query.m)
const unarchivedDegreeTemplates = computed(() => _filter(degreeTemplates.value, t => !t.archivedAt))

contextStore.loadingStart()

onMounted(() => {
  getDegreeTemplates().then(data => {
    degreeTemplates.value = data
    contextStore.loadingComplete()
  })
})

const onUpdateDegreeTemplate = degreeTemplate => {
  const index = degreeTemplates.value.findIndex(d => d.id === degreeTemplate.id)
  if (degreeTemplate.deletedAt) {
    degreeTemplates.value.splice(index, 1)
  } else {
    degreeTemplates.value = sortBy(degreeTemplates.value.concat([degreeTemplate]), 'name')
  }
}
</script>

<style scoped>
.show-hide-archived-btn {
  margin-left: -16px;
}
</style>
