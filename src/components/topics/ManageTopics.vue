<template>
  <div v-if="topics">
    <div class="pb-3 pl-3 pt-2 w-50">
      <b-input-group size="sm">
        <b-form-input
          id="filter-topics"
          v-model="filter"
          type="search"
          placeholder="Search"></b-form-input>
        <b-input-group-append>
          <b-button :disabled="!filter" @click="filter = ''">Clear</b-button>
        </b-input-group-append>
      </b-input-group>
    </div>
    <b-table
      show-empty
      empty-filtered-text="No topic matches your search."
      :items="topics"
      :fields="fields"
      :filter="filter"
      :filter-included-fields="['topic']"
      sticky-header
      thead-class="sortable-table-header border-bottom">
      <template v-slot:cell(topic)="row">
        <span :class="{'faint-text': !!row.item.deletedAt}">
          {{ row.item.topic }} <span v-if="row.item.deletedAt" class="has-error">[DELETED]</span>
        </span>
      </template>
      <template v-slot:cell(actions)="row">
        <div class="d-flex justify-content-end">
          <b-button class="pr-2" variant="link" @click="edit(row.item)">
            Edit
          </b-button>
          <b-button
            v-if="row.item.deletedAt"
            class="p-0"
            variant="link"
            @click="undelete(row.item)">
            Undelete
          </b-button>
          <b-button
            v-if="!row.item.deletedAt"
            class="p-0"
            variant="link"
            @click="openDeleteTopicModal(row.item)">
            Delete
          </b-button>
        </div>
      </template>
    </b-table>
    <EditTopicModal v-if="isEditTopicModalOpen" :topic="topicEdit" />
    <AreYouSureModal
      v-if="isDeleteTopicModalOpen"
      :function-cancel="deleteCancel"
      :function-confirm="deleteConfirm"
      :modal-body="`Are you sure you want to delete <b>'${topicDelete.topic}'</b>?`"
      :show-modal="isDeleteTopicModalOpen"
      button-label-confirm="Delete"
      modal-header="Delete Topic" />
  </div>
</template>

<script>
import AreYouSureModal from '@/components/util/AreYouSureModal';
import Context from '@/mixins/Context';
import EditTopicModal from '@/components/topics/EditTopicModal';
import {deleteTopic, getAllTopics, undeleteTopic} from '@/api/topics';

export default {
  name: 'ManageTopics',
  components: {AreYouSureModal, EditTopicModal},
  mixins: [Context],
  data() {
    return {
      fields: [
        {key: 'topic', label: 'Label', sortable: true},
        {key: 'availableInAppointments', label: 'Appointments', formatter: value => value ? 'Yes' : 'No', sortable: true},
        {key: 'availableInNotes', label: 'Notes', formatter: value => value ? 'Yes' : 'No', sortable: true},
        {key: 'actions', label: ''}
      ],
      filter: null,
      isDeleteTopicModalOpen: false,
      isEditTopicModalOpen: false,
      topicDelete: undefined,
      topicEdit: undefined,
      topics: undefined
    }
  },
  mounted() {
    getAllTopics(true).then(data => {
      this.topics = data;
    })
  },
  methods: {
    deleteCancel() {
      this.isDeleteTopicModalOpen = false;
      this.topicDelete = undefined;
    },
    deleteConfirm() {
      deleteTopic(this.topicDelete.id).then(() => {
        this.isDeleteTopicModalOpen = false;
        this.topicDelete = undefined;
        // TODO: screenreader
      })
    },
    openDeleteTopicModal(topic) {
      this.topicDelete = topic;
      this.isDeleteTopicModalOpen = true;
    },
    edit(topic) {
      this.topicEdit = topic;
      this.isEditTopicModalOpen = true;
    },
    undelete(topic) {
      undeleteTopic(topic.id).then(() => {
        // TODO: screenreader
      })
    }
  }
}
</script>
