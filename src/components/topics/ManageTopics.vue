<template>
  <div v-if="hasLoadedTopics">
    <div class="d-flex justify-content-between">
      <div class="pb-3 pl-3 pt-2 w-50">
        <v-text-field
          v-model="filter"
          class="d-inline"
          density="compact"
          label="Search"
          variant="outlined"
        >
        </v-text-field>
      </div>

      <div class="pr-3 pt-2">
        <v-btn
          class="ml-2"
          @click="filter = ''"
        >
          Clear
        </v-btn>
      </div>
    </div>

    <v-btn
      id="new-note-button"
      class="p-0 pb-1"
      :disabled="isEditTopicModalOpen"
      @click="openCreateTopicModal"
    >
      <v-icon :icon="mdiPlusBox"></v-icon>
      Create New Topic
    </v-btn>

    <div class="pt-2">
      <v-table
        density="compact"
        height="350px"
        fixed-header
      >
        <thead>
          <tr>
            <th class="border-top-0"><span>Topic</span></th>
            <th class="border-top-0"><span>Deleted?</span></th>
            <th class="border-top-0"><span>Usage</span></th>
            <th class="border-top-0"><span>Actions</span></th>
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
                :icon="mdiTrashCanOutline"
                density="compact"
                @click="openDeleteTopicModal(item)"
              >
              </v-btn>

              <v-btn
                v-if="item.deletedAt"
                :icon="mdiDeleteRestore"
                density="compact"
                @click="undelete(item)"
              >
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
      v-if="isDeleteTopicModalOpen"
      :function-cancel="deleteCancel"
      :function-confirm="deleteConfirm"
      :show-modal="isDeleteTopicModalOpen"
      button-label-confirm="Delete"
      modal-header="Delete Topic"
    >
      <span> Are you sure you want to delete <b>{{ topicDelete.topic }}</b>? </span>
    </AreYouSureModal>
  </div>
</template>

<script setup>
import {mdiDeleteRestore} from '@mdi/js'
import {mdiTrashCanOutline} from '@mdi/js'
import {mdiPlusBox} from '@mdi/js'
import {useContextStore} from '@/stores/context'

</script>

<script>
import AreYouSureModal from '@/components/util/AreYouSureModal'
// import Context from '@/mixins/Context'
import EditTopicModal from '@/components/topics/EditTopicModal'
import Util from '@/mixins/Util'
import {deleteTopic, getAllTopics, getUsageStatistics, undeleteTopic} from '@/api/topics'
import {putFocusNextTick} from '@/lib/utils'
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
      topics: undefined
    }
  },
  computed: {
    filteredTable() {
      if (this.filter === null) {
        return this.topics
      }
      return this.topics.filter(item => item.topic.toLowerCase().includes(this.filter.toLowerCase()))
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
        useContextStore().alertScreenReader(`Topic '${topic.topic}' updated.`)
        putFocusNextTick(focusTarget)
      } else {
        this.refresh(focusTarget)
        useContextStore().alertScreenReader(`Topic '${topic.topic}' created.`)
      }
      this.topicEdit = null
      this.isEditTopicModalOpen = false
    },
    formatBoolean: value => value ? 'Yes' : 'No',
    deleteCancel() {
      this.isDeleteTopicModalOpen = false
      this.topicDelete = undefined
      useContextStore().alertScreenReader('Canceled')
      putFocusNextTick('filter-topics')
    },
    deleteConfirm() {
      return deleteTopic(this.topicDelete.id).then(() => {
        this.isDeleteTopicModalOpen = false
        this.topicDelete.deletedAt = DateTime.now()
        useContextStore().alertScreenReader(`Topic '${this.topicDelete.topic}' deleted.`)
        putFocusNextTick(`topic-${this.topicDelete.id}`)
        this.topicDelete = undefined
      })
    },
    onCancelEdit() {
      this.isEditTopicModalOpen = false
      useContextStore().alertScreenReader('Canceled')
      putFocusNextTick('filter-topics')
      this.topicEdit = null
    },
    openCreateTopicModal() {
      this.topicEdit = {
        topic: ''
      }
      this.isEditTopicModalOpen = true
      useContextStore().alertScreenReader('Opened modal to create new topic.')
    },
    openDeleteTopicModal(topic) {
      this.topicDelete = topic
      this.isDeleteTopicModalOpen = true
      useContextStore().alertScreenReader('Opened modal to confirm delete.')
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
        useContextStore().alertScreenReader(`Topic ${topic.topic} un-deleted.`)
        putFocusNextTick(`topic-${topic.id}`)
      })
    }
  }
}
</script>
