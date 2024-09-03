<template>
  <div v-if="hasLoadedTopics">
    <div class="align-center d-flex justify-space-between">
      <div class="w-50">
        <v-text-field
          id="filter-topics"
          v-model="filter"
          class="d-inline"
          density="compact"
          hide-details
          label="Search"
          variant="outlined"
        />
      </div>

      <v-btn
        class="button-position ml-2 mr-4"
        color="primary"
        :disabled="!filter"
        @click="filter = ''"
      >
        Clear
      </v-btn>
      <v-btn
        id="create-topic-button"
        class="mr-3"
        color="primary"
        :disabled="isEditTopicModalOpen"
        @click="openCreateTopicModal"
      >
        <v-icon class="mr-1" :icon="mdiPlusBox" />
        Create New Topic
      </v-btn>
    </div>

    <div class="border-b-sm mt-4">
      <v-table
        density="compact"
        height="200px"
        hover
        fixed-header
      >
        <thead>
          <tr>
            <th class="border-top-0 text-h6 cursor-pointer" @click="setTableSort('topic')">
              <span>Topic</span>
              <template v-if="sortBy === 'topic'">
                <v-icon v-if="sortByMap.get('topic') === true" class="position-absolute mb-1" :icon="mdiMenuDown" />
                <v-icon v-if="sortByMap.get('topic') === false" class="position-absolute mb-1" :icon="mdiMenuUp" />
              </template>
            </th>
            <th class="border-top-0 text-h6 cursor-pointer" @click="setTableSort('deleted')">
              <span>Deleted?</span>
              <template v-if="sortBy === 'deleted'">
                <v-icon v-if="sortByMap.get('deleted') === false" class="position-absolute mb-1" :icon="mdiMenuDown" />
                <v-icon v-if="sortByMap.get('deleted') === true" class="position-absolute mb-1" :icon="mdiMenuUp" />
              </template>
            </th>
            <th class="border-top-0 text-h6 cursor-pointer" @click="setTableSort('usage')">
              <span>Usage</span>
              <template v-if="sortBy === 'usage'">
                <v-icon v-if="sortByMap.get('usage') === true" class="position-absolute mb-1" :icon="mdiMenuDown" />
                <v-icon v-if="sortByMap.get('usage') === false" class="position-absolute mb-1" :icon="mdiMenuUp" />
              </template>
            </th>
            <th class="border-top-0 text-h6 cursor-pointer" @click="setTableSort('deleted')">
              <span>Actions</span>
              <template v-if="sortBy === 'deleted'">
                <v-icon v-if="sortByMap.get('deleted') === false" class="position-absolute mb-1" :icon="mdiMenuDown" />
                <v-icon v-if="sortByMap.get('deleted') === true" class="position-absolute mb-1" :icon="mdiMenuUp" />
              </template>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="item in filteredTable"
            :key="item.name"
          >
            <td>{{ item.topic }}</td>
            <td>{{ item.deletedAt ? 'Yes' : 'No' }}</td>
            <td>{{ item.countNotes }}</td>
            <td>
              <v-btn
                v-if="!item.deletedAt"
                density="compact"
                variant="flat"
                @click="openDeleteTopicModal(item)"
              >
                <v-icon :icon="mdiTrashCan" />
                <v-tooltip
                  activator="parent"
                  location="start"
                >
                  Delete
                </v-tooltip>
              </v-btn>

              <v-btn
                v-if="item.deletedAt"
                density="compact"
                variant="flat"
                @click="undelete(item)"
              >
                <v-icon :icon="mdiDeleteRestore" color="warning" />
                <v-tooltip
                  activator="parent"
                  location="start"
                >
                  Undelete
                </v-tooltip>
              </v-btn>
            </td>
          </tr>
        </tbody>
      </v-table>
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
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {computed, onMounted, ref} from 'vue'
import {DateTime} from 'luxon'
import {deleteTopic, getAllTopics, getUsageStatistics, undeleteTopic} from '@/api/topics'
import {each, find, get, toLower} from 'lodash'
import {
  mdiDeleteRestore,
  mdiMenuDown,
  mdiMenuUp,
  mdiPlusBox,
  mdiTrashCan
} from '@mdi/js'

const filter = ref(undefined)
const hasLoadedTopics = ref(false)
const isDeleteTopicModalOpen = ref(false)
const isEditTopicModalOpen = ref(false)
const topicDelete = ref(undefined)
const topicEdit = ref(undefined)
const topics = ref(undefined)
const sortBy = ref('topic')
const sortByMap = new Map([
  ['topic', false],
  ['deleted', false],
  ['usage', false]
])

const filteredTable = computed(() => {
  if (sortBy.value) {
    if (filter.value === null) {
      return sortTable(topics.value)
    }
    return sortTable(topics.value.filter(item => toLower(item.topic).includes(toLower(filter.value))))
  } else {
    return topics.value
  }
})

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
  return deleteTopic(topicDelete.value.id).then(() => {
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
      hasLoadedTopics.value = true
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

const setTableSort = filterBy => {
  sortBy.value = filterBy
  sortByMap.value.set(sortBy.value, !sortByMap.value.get(sortBy.value))
}

const sortTable = sortByArr => {
  const newArr = []
  switch (sortBy.value) {
  case 'topic':
    return !get(sortByMap.value, 'topic') ? sortByArr.sort((a,b) => (toLower(a.topic) > toLower(b.topic)) ? 1 : ((toLower(b.topic) > toLower(a.topic)) ? -1 : 0)) : sortByArr.sort((a,b) => (toLower(a.topic) < toLower(b.topic)) ? 1 : ((toLower(b.topic) < toLower(a.topic)) ? -1 : 0))

  case 'deleted':
    if (!sortByMap.value.get('deleted')) {
      sortByArr.forEach(item => {
        if (item.deletedAt) {
          newArr.push(item)
        }
      })

      sortByArr.forEach(item => {
        if (!item.deletedAt) {
          newArr.push(item)
        }
      })
    } else {
      sortByArr.forEach(item => {
        if (!item.deletedAt) {
          newArr.push(item)
        }
      })
      sortByArr.forEach(item => {
        if (item.deletedAt) {
          newArr.push(item)
        }
      })
    }
    return newArr

  case 'usage':
    return !sortByMap.value.get('usage') ? sortByArr.sort((a,b) => a.countNotes - b.countNotes) : sortByArr.sort((a,b) => b.countNotes - a.countNotes)

  default:
    return !sortByMap.value.get('topic') ? sortByArr.sort((a,b) => (a.topic > b.topic) ? 1 : ((b.topic > a.topic) ? -1 : 0)) : sortByArr.sort((a,b) => (a.topic < b.topic) ? 1 : ((b.topic < a.topic) ? -1 : 0))
  }
}
</script>
