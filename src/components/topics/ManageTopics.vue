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
        id="new-note-button"
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
import {
  mdiDeleteRestore,
  mdiMenuDown,
  mdiMenuUp,
  mdiPlusBox,
  mdiTrashCan
} from '@mdi/js'
</script>

<script>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import EditTopicModal from '@/components/topics/EditTopicModal'
import Util from '@/mixins/Util'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {deleteTopic, getAllTopics, getUsageStatistics, undeleteTopic} from '@/api/topics'
import {DateTime} from 'luxon'

export default {
  name: 'ManageTopics',
  components: {AreYouSureModal, EditTopicModal},
  mixins: [Util],
  data() {
    return {
      fields: [
        {
          key: 'topic',
          label: 'Label',
          sortable: true,
          tdClass: 'align-middle'
        },
        {
          formatter: this.formatBoolean,
          key: 'deletedAt',
          label: 'Deleted?',
          sortable: true,
          tdClass: 'align-middle mr-3 pr-5 text-right',
          thClass: 'text-center'
        },
        {
          formatter: n => this.numFormat(n),
          key: 'countNotes',
          label: 'Usage',
          sortable: true,
          tdClass: 'align-middle pr-5 service-announcement text-nowrap text-right text-white',
          thClass: 'text-right'
        },
        {
          key: 'actions',
          label: 'Actions',
          sortable: false,
          tdClass: 'align-middle text-right',
          thClass: 'text-right'
        }
      ],
      filter: null,
      hasLoadedTopics: false,
      isDeleteTopicModalOpen: false,
      isEditTopicModalOpen: false,
      topicDelete: undefined,
      topicEdit: undefined,
      topics: undefined,
      sortBy: 'topic',
      sortByMap: new Map([
        ['topic', false],
        ['deleted', false],
        ['usage', false]
      ])
    }
  },
  computed: {
    filteredTable() {
      if (this.sortBy) {
        if (this.filter === null) {
          return this.sortTable(this.topics)
        }
        return this.sortTable(this.topics.filter(item => item.topic.toLowerCase().includes(this.filter.toLowerCase())))
      } else {
        return this.topics
      }
    },
  },
  mounted() {
    this.refresh()
  },
  methods: {
    afterSaveTopic(topic) {
      const match = this._find(this.topics, ['id', topic.id])
      const focusTarget = `topic-${topic.id}`
      if (match) {
        Object.assign(match, topic)
        alertScreenReader(`Topic '${topic.topic}' updated.`)
        putFocusNextTick(focusTarget)
      } else {
        this.refresh(focusTarget)
        alertScreenReader(`Topic '${topic.topic}' created.`)
      }
      this.topicEdit = null
      this.isEditTopicModalOpen = false
    },
    formatBoolean: value => value ? 'Yes' : 'No',
    deleteCancel() {
      this.isDeleteTopicModalOpen = false
      this.topicDelete = undefined
      alertScreenReader('Canceled')
      putFocusNextTick('filter-topics')
    },
    deleteConfirm() {
      return deleteTopic(this.topicDelete.id).then(() => {
        this.isDeleteTopicModalOpen = false
        this.topicDelete.deletedAt = DateTime.now()
        alertScreenReader(`Topic '${this.topicDelete.topic}' deleted.`)
        putFocusNextTick(`topic-${this.topicDelete.id}`)
        this.topicDelete = undefined
      })
    },
    onCancelEdit() {
      this.isEditTopicModalOpen = false
      alertScreenReader('Canceled')
      putFocusNextTick('filter-topics')
      this.topicEdit = null
    },
    openCreateTopicModal() {
      this.topicEdit = {
        topic: ''
      }
      this.isEditTopicModalOpen = true
      alertScreenReader('Opened modal to create new topic.')
    },
    openDeleteTopicModal(topic) {
      this.topicDelete = topic
      this.isDeleteTopicModalOpen = true
      alertScreenReader('Opened modal to confirm delete.')
    },
    refresh(focusTarget) {
      getAllTopics(true).then(data => {
        this.topics = data
        getUsageStatistics().then(statistics => {
          this._each(this.topics, topic => {
            topic.countNotes = statistics.notes[topic.id] || 0
          })
          this.hasLoadedTopics = true
          putFocusNextTick(focusTarget)
        })
      })
    },
    undelete(topic) {
      undeleteTopic(topic.id).then(() => {
        topic.deletedAt = null
        alertScreenReader(`Topic ${topic.topic} un-deleted.`)
        putFocusNextTick(`topic-${topic.id}`)
      })
    },
    setTableSort(filterBy) {
      this.sortBy = filterBy
      this.sortByMap.set(this.sortBy, !this.sortByMap.get(this.sortBy))
    },
    sortTable(sortByArr) {
      const newArr = []
      switch (this.sortBy) {
      case 'topic':
        return !this.sortByMap.get('topic') ? sortByArr.sort((a,b) => (a.topic.toLowerCase() > b.topic.toLowerCase()) ? 1 : ((b.topic.toLowerCase() > a.topic.toLowerCase()) ? -1 : 0)) : sortByArr.sort((a,b) => (a.topic.toLowerCase() < b.topic.toLowerCase()) ? 1 : ((b.topic.toLowerCase() < a.topic.toLowerCase()) ? -1 : 0))

      case 'deleted':
        if (!this.sortByMap.get('deleted')) {
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
        return !this.sortByMap.get('usage') ? sortByArr.sort((a,b) => a.countNotes - b.countNotes) : sortByArr.sort((a,b) => b.countNotes - a.countNotes)

      default:
        return !this.sortByMap.get('topic') ? sortByArr.sort((a,b) => (a.topic > b.topic) ? 1 : ((b.topic > a.topic) ? -1 : 0)) : sortByArr.sort((a,b) => (a.topic < b.topic) ? 1 : ((b.topic < a.topic) ? -1 : 0))
      }
    }
  }
}
</script>


<style scoped>
#new-note-button {
  margin-left: auto;
}
</style>
