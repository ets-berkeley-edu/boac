<template>
  <div>
    <div :class="{'truncate': !isOpen}">
      <span v-if="size(note.message)" v-html="note.message"></span>
      <span v-if="!size(note.message)">{{ note.category }}, {{ note.subcategory }}</span>
    </div>
    <div v-if="author" class="mt-3">
      <a
        :aria-label="`Go to UC Berkeley Directory page of ${author.firstName} ${author.lastName}`"
        :href="`https://www.berkeley.edu/directory/results?search-term=${author.firstName}%20${author.lastName}`"
        target="_blank">{{ author.firstName }} {{ author.lastName }}</a>
    </div>
    <div v-if="size(note.topics)">
      <div class="pill-list-header mt-3 mb-1">{{ size(note.topics) === 1 ? 'Topic' : 'Topics' }}</div>
      <ul class="pill-list pl-0">
        <li v-for="topic in note.topics" :key="topic" class="mt-2">
          <span class="pill text-uppercase text-nowrap">{{ topic }}</span>
        </li>
      </ul>
    </div>
    <div v-if="size(note.attachments)">
      <div class="pill-list-header mt-3 mb-1">{{ size(note.attachments) === 1 ? 'Attachment' : 'Attachments' }}</div>
      <ul class="pill-list pl-0">
        <li v-for="attachment in note.attachments" :key="attachment" class="mt-2">
          <a href="#" class="pill text-nowrap"><i class="fas fa-paperclip"></i> {{ attachment }}</a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import store from '@/store'
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'AdvisingNote',
  mixins: [UserMetadata, Util],
  props: {
    isOpen: Boolean,
    note: Object
  },
  data: () => ({
    allUsers: undefined,
    author: undefined
  }),
  watch: {
    isOpen(open) {
      if (open && this.isUndefined(this.author) && this.note.advisorSid) {
        store.dispatch('user/loadCalnetUserByCsid', this.note.advisorSid).then(data => {
          this.author = data;
        });
      }
    }
  }
}
</script>

<style scoped>
.pill {
  background-color: #fff;
  border: 1px solid #666;
  border-radius: 5px;
  color: #666;
  font-size: 12px;
  height: 26px;
  padding: 6px;
  width: auto;
}
.pill-list {
  list-style-type: none;
}
.pill-list-header {
  font-size: 16px;
  font-weight: 800;
}
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
