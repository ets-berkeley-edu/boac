<template>
  <div v-if="hasLoadedTopics">
    <div class="d-flex justify-content-between">
      <div class="pb-3 pl-3 pt-2 w-50">
        <b-input-group size="sm">
          <b-form-input
            id="filter-topics"
            v-model="filter"
            type="search"
            placeholder="Search"
          ></b-form-input>
          <b-input-group-append>
            <b-button :disabled="!filter" @click="filter = ''">Clear</b-button>
          </b-input-group-append>
        </b-input-group>
      </div>
      <div class="pr-3 pt-3">
        <b-btn
          id="new-note-button"
          class="p-0 pb-1"
          :disabled="isEditTopicModalOpen"
          variant="link"
          @click="openCreateTopicModal"
        >
          <font-awesome icon="plus-square" />
          Create New Topic
        </b-btn>
      </div>
    </div>
    <div class="pt-2">
      <b-table
        empty-filtered-text="No topic matches your search."
        :fields="fields"
        :filter="filter"
        :filter-included-fields="['topic']"
        :items="topics"
        :no-border-collapse="true"
        show-empty
        sticky-header
        thead-class="sortable-table-header border-bottom"
      >
        <template v-slot:thead-top="{}">
          <b-tr>
            <b-th class="border-top-0"><span class="sr-only">Topic</span></b-th>
            <b-th class="border-top-0"><span class="sr-only">Deleted?</span></b-th>
            <b-th class="border-top-0"></b-th>
          </b-tr>
        </template>
        <template v-slot:cell(actions)="row">
          <div class="d-flex justify-content-end">
            <b-button
              v-if="row.item.deletedAt"
              class="pr-0"
              variant="link"
              @click="undelete(row.item)"
            >
              <font-awesome
                aria-label="Un-delete"
                class="text-warning"
                icon="trash-restore"
                title="Un-delete"
              />
            </b-button>
            <b-button
              v-if="!row.item.deletedAt"
              class="pr-0"
              variant="link"
              @click="openDeleteTopicModal(row.item)"
            >
              <font-awesome
                icon="trash-alt"
                aria-label="Delete"
                class="text-secondary"
                title="Delete"
              />
            </b-button>
          </div>
        </template>
      </b-table>
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
      :modal-body="`Are you sure you want to delete <b>'${topicDelete.topic}'</b>?`"
      :show-modal="isDeleteTopicModalOpen"
      button-label-confirm="Delete"
      modal-header="Delete Topic"
    />
  </div>
</template>

<script>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import Context from '@/mixins/Context'
import EditTopicModal from '@/components/topics/EditTopicModal'
import Util from '@/mixins/Util'
import {deleteTopic, getAllTopics, getUsageStatistics, undeleteTopic} from '@/api/topics'

export default {
  name: 'ManageTopics',
  components: {AreYouSureModal, EditTopicModal},
  mixins: [Context, Util],
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
  mounted() {
    this.refresh()
  },
  methods: {
    afterSaveTopic(topic) {
      const match = this._find(this.topics, ['id', topic.id])
      const focusTarget = `topic-${topic.id}`
      if (match) {
        Object.assign(match, topic)
        this.$announcer.polite(`Topic '${topic.topic}' updated.`)
        this.$putFocusNextTick(focusTarget)
      } else {
        this.refresh(focusTarget)
        this.$announcer.polite(`Topic '${topic.topic}' created.`)
      }
      this.topicEdit = null
      this.isEditTopicModalOpen = false
    },
    formatBoolean: value => value ? 'Yes' : 'No',
    deleteCancel() {
      this.isDeleteTopicModalOpen = false
      this.topicDelete = undefined
      this.$announcer.polite('Canceled')
      this.$putFocusNextTick('filter-topics')
    },
    deleteConfirm() {
      return deleteTopic(this.topicDelete.id).then(() => {
        this.isDeleteTopicModalOpen = false
        this.topicDelete.deletedAt = this.$moment()
        this.$announcer.polite(`Topic '${this.topicDelete.topic}' deleted.`)
        this.$putFocusNextTick(`topic-${this.topicDelete.id}`)
        this.topicDelete = undefined
      })
    },
    onCancelEdit() {
      this.isEditTopicModalOpen = false
      this.$announcer.polite('Canceled')
      this.$putFocusNextTick('filter-topics')
      this.topicEdit = null
    },
    openCreateTopicModal() {
      this.topicEdit = {
        topic: ''
      }
      this.isEditTopicModalOpen = true
      this.$announcer.polite('Opened modal to create new topic.')
    },
    openDeleteTopicModal(topic) {
      this.topicDelete = topic
      this.isDeleteTopicModalOpen = true
      this.$announcer.polite('Opened modal to confirm delete.')
    },
    refresh(focusTarget) {
      getAllTopics(true).then(data => {
        this.topics = data
        getUsageStatistics().then(statistics => {
          this._each(this.topics, topic => {
            topic.countNotes = statistics.notes[topic.id] || 0
          })
          this.hasLoadedTopics = true
          this.$putFocusNextTick(focusTarget)
        })
      })
    },
    undelete(topic) {
      undeleteTopic(topic.id).then(() => {
        topic.deletedAt = null
        this.$announcer.polite(`Topic ${topic.topic} un-deleted.`)
        this.$putFocusNextTick(`topic-${topic.id}`)
      })
    }
  }
}
</script>
