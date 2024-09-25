<template>
  <div v-if="!isNil(topics)">
    <div class="align-center d-flex justify-space-between">
      <div class="align-center d-flex flex-nowrap w-66">
        <div class="w-66">
          <v-text-field
            id="filter-topics"
            v-model="filter"
            autocomplete="off"
            class="d-inline"
            clearable
            density="compact"
            hide-details
            label="Search"
            variant="outlined"
          />
        </div>
        <v-btn
          id="clear-topic-search"
          class="button-position ml-2 mr-4"
          color="primary"
          :disabled="!filter"
          text="Clear"
          @click="filter = ''"
        />
      </div>
      <v-btn
        id="create-topic-button"
        class="mr-3"
        color="primary"
        :disabled="isEditTopicModalOpen"
        :prepend-icon="mdiPlusBox"
        text="Create New Topic"
        @click="openCreateTopicModal"
      />
    </div>
    <div class="border-b-sm mt-6">
      <v-data-table
        density="compact"
        fixed-header
        :headers="headers"
        :header-props="{class: 'data-table-header-cell'}"
        hide-default-footer
        hide-no-data
        hover
        :items="topics"
        :items-per-page="-1"
        mobile-breakpoint="md"
        :row-props="row => ({id: `row-topic-${normalizeId(row.item.topic)}`})"
      >
        <template #item.deletedAt="{item}">
          <div class="float-right" :class="{'font-weight-medium text-red': item.deletedAt}">
            {{ item.deletedAt ? 'Yes' : 'No' }}
          </div>
        </template>
        <template #item.actions="{item}">
          <v-tooltip text="Delete">
            <template #activator="{props}">
              <v-btn
                v-if="!item.deletedAt"
                v-bind="props"
                density="compact"
                :icon="mdiTrashCan"
                variant="plain"
                @click="openDeleteTopicModal(item)"
              />
            </template>
          </v-tooltip>
          <v-tooltip text="Undelete">
            <template #activator="{props}">
              <v-btn
                v-if="item.deletedAt"
                v-bind="props"
                color="warning"
                density="compact"
                :icon="mdiDeleteRestore"
                variant="plain"
                @click="undelete(item)"
              />
            </template>
          </v-tooltip>
        </template>
      </v-data-table>
    </div>
    <EditTopicModal
      v-if="isEditTopicModalOpen"
      :after-save="afterSaveTopic"
      :all-topics="topics"
      :on-cancel="onCancelEdit"
    />
    <AreYouSureModal
      v-model="isDeleteTopicModalOpen"
      button-label-confirm="Delete"
      :function-cancel="deleteCancel"
      :function-confirm="deleteConfirm"
      modal-header="Delete Topic"
    >
      <span v-if="topicDelete"> Are you sure you want to delete <b>{{ topicDelete.topic }}</b>? </span>
    </AreYouSureModal>
  </div>
</template>

<script setup>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import EditTopicModal from '@/components/topics/EditTopicModal'
import {alertScreenReader, normalizeId, putFocusNextTick} from '@/lib/utils'
import {DateTime} from 'luxon'
import {deleteTopic, getAllTopics, getUsageStatistics, undeleteTopic} from '@/api/topics'
import {each, find, isNil} from 'lodash'
import {
  mdiDeleteRestore,
  mdiPlusBox,
  mdiTrashCan
} from '@mdi/js'
import {onMounted, ref} from 'vue'

const filter = ref(undefined)
const headers = [
  {align: 'start', key: 'topic', title: 'Topic', width: '60%'},
  {align: 'end', key: 'deletedAt', title: 'Deleted?'},
  {align: 'end', key: 'countNotes', title: 'Usage'},
  {align: 'end', key: 'actions', sortable: false},
]
const isDeleteTopicModalOpen = ref(false)
const isEditTopicModalOpen = ref(false)
const topicDelete = ref(undefined)
const topicEdit = ref(undefined)
const topics = ref(undefined)

onMounted(() => {
  refresh()
})

const afterSaveTopic = topic => {
  const match = find(topics.value, ['id', topic.id])
  const focusTarget = `topic-${topic.id}`
  if (match) {
    Object.assign(match, topic)
    alertScreenReader(`Topic '${topic.topic}' updated.`)
    putFocusNextTick(focusTarget)
  } else {
    refresh(focusTarget)
    alertScreenReader(`Topic '${topic.topic}' created.`)
    putFocusNextTick('create-topic-button')
  }
  topicEdit.value = null
  isEditTopicModalOpen.value = false
}

const deleteCancel = () => {
  isDeleteTopicModalOpen.value = false
  topicDelete.value = undefined
  alertScreenReader('Canceled')
  putFocusNextTick('filter-topics')
}

const deleteConfirm = () => {
  deleteTopic(topicDelete.value.id).then(() => {
    isDeleteTopicModalOpen.value = false
    topicDelete.value.deletedAt = DateTime.now()
    alertScreenReader(`Topic '${topicDelete.value.topic}' deleted.`)
    putFocusNextTick(`topic-${topicDelete.value.id}`)
    topicDelete.value = undefined
  })
}

const onCancelEdit = () => {
  isEditTopicModalOpen.value = false
  alertScreenReader('Canceled')
  putFocusNextTick('filter-topics')
  topicEdit.value = null
}

const openCreateTopicModal = () => {
  topicEdit.value = {
    topic: ''
  }
  isEditTopicModalOpen.value = true
  alertScreenReader('Opened modal to create new topic.')
}

const openDeleteTopicModal = topic => {
  topicDelete.value = topic
  isDeleteTopicModalOpen.value = true
  alertScreenReader('Opened modal to confirm delete.')
}

const refresh = focusTarget => {
  getAllTopics(true).then(data => {
    topics.value = data
    getUsageStatistics().then(statistics => {
      each(topics.value, topic => topic.countNotes = statistics.notes[topic.id] || 0)
      putFocusNextTick(focusTarget)
    })
  })
}

const undelete = topic => {
  undeleteTopic(topic.id).then(() => {
    topic.deletedAt = null
    alertScreenReader(`Topic ${topic.topic} un-deleted.`)
    putFocusNextTick(`topic-${topic.id}`)
  })
}
</script>

<style>
tbody tr:nth-of-type(odd) {
 background-color: rgb(var(--v-theme-surface-light))
}
.data-table-header-cell {
  font-size: 14px;
  font-weight: bold;
  height: 32px !important;
}
</style>
