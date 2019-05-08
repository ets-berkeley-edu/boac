<template>
  <div>
    <div>
      <label id="add-note-topic-label" class="font-weight-bold mt-2" for="add-note-topic">
        Topic Categories
      </label>
    </div>
    <b-container class="pl-0 ml-0">
      <b-form-row class="pb-1">
        <b-col cols="4">
          <b-input-group>
            <b-input-group-text
              id="add-topic-button"
              slot="append"
              class="btn-add-topic"
              @click="addTopic">
              <i class="fas fa-plus pr-1"></i>Add
            </b-input-group-text>
            <b-form-input
              id="add-note-topic"
              v-model="topic"
              aria-labelledby="add-note-topic-label"
              type="text"
              maxlength="255"
              list="add-topic-input-list"
              @keydown.enter="addTopic">
            </b-form-input>
            <b-form-datalist id="add-topic-input-list" :options="suggestedTopics"></b-form-datalist>
          </b-input-group>
        </b-col>
      </b-form-row>
      <div>
        <ul class="pill-list pl-0">
          <li
            v-for="(topic, index) in topics"
            :key="index">
            <span class="pill pill-attachment text-uppercase text-nowrap">
              {{ topic }}
              <b-btn
                :id="`remove-topic-${index}`"
                variant="link"
                class="px-0 pt-1"
                @click.prevent="functionRemove">
                <i class="fas fa-times-circle has-error pl-2"></i>
              </b-btn>
            </span>
          </li>
        </ul>
      </div>
    </b-container>
  </div>
</template>

<script>
export default {
  name: 'AdvisingNoteTopics',
  props: {
    functionAdd: {
      type: Function,
      required: true
    },
    functionRemove: {
      type: Function,
      required: true
    },
    suggestedTopics: {
      type: Array,
      required: false
    },
    topics: {
      type: Array,
      required: true
    }
  },
  data: () => ({
    topic: undefined
  }),
  methods: {
    addTopic() {
      if (this.topic && this.topic.trim()) {
        this.functionAdd(this.topic);
      }
      this.topic = undefined;
    }
  }
}
</script>

<style scoped>
.btn-add-topic:not(:disabled) {
  cursor: pointer;
}
.btn-add-topic:hover,
.btn-add-topic:focus,
.btn-add-topic:active
{
  color: #333;
  background-color: #aaa;
}
</style>