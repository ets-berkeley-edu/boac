<template>
  <div>
    <div :id="`note-${note.id}-message-closed`" :class="{'truncate': !isOpen}">
      <span v-if="note.subject">{{ note.subject }}</span>
      <span v-if="!note.subject && size(note.message)" v-html="note.message"></span>
      <span v-if="!note.subject && !size(note.message)">{{ note.category }}, {{ note.subcategory }}</span>
    </div>
    <div v-if="isOpen && note.subject && note.message" class="mt-2">
      <span :id="`note-${note.id}-message-open`" v-html="note.message"></span>
    </div>
    <div v-if="author" class="mt-2">
      <div>
        <a
          :id="`note-${note.id}-author-name`"
          :aria-label="`Go to UC Berkeley Directory page of ${author.firstName} ${author.lastName}`"
          :href="`https://www.berkeley.edu/directory/results?search-term=${getName(author)}`"
          target="_blank">{{ getName(author) }}</a>
        <span v-if="author.role">
          - <span :id="`note-${note.id}-author-role`" class="text-dark">{{ author.role }}</span>
        </span>
      </div>
      <div v-if="size(author.depts)" class="text-secondary">
        <span v-if="note.isLegacy">(currently </span><span v-for="(dept, index) in author.depts" :key="dept">
          <span :id="`note-${note.id}-author-dept-${index}`">{{ dept }}</span>
        </span><span v-if="note.isLegacy">)</span>
      </div>
    </div>
    <div v-if="size(note.topics)">
      <div class="pill-list-header mt-3 mb-1">{{ size(note.topics) === 1 ? 'Topic' : 'Topics' }}</div>
      <ul class="pill-list pl-0">
        <li
          v-for="(topic, index) in note.topics"
          :id="`note-${note.id}-topic-${index}`"
          :key="topic"
          class="mt-2">
          <span class="pill text-uppercase text-nowrap">{{ topic }}</span>
        </li>
      </ul>
    </div>
    <div v-if="size(note.attachments)">
      <div class="pill-list-header mt-3 mb-1">{{ size(note.attachments) === 1 ? 'Attachment' : 'Attachments' }}</div>
      <ul class="pill-list pl-0">
        <li v-for="(attachment, index) in note.attachments" :key="attachment" class="mt-2">
          <a :id="`note-${note.id}-attachment-${index}`" href="#" class="pill text-nowrap"><i class="fas fa-paperclip"></i> {{ attachment }}</a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import store from '@/store'
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { getUserByUid } from '@/api/user';

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
      if (open && this.isUndefined(this.author)) {
        if (this.note.author.name) {
          this.author = this.note.author;
        } else {
          const author_uid = this.note.author.uid;
          if (author_uid) {
            if (author_uid === this.user.uid) {
              this.author = this.user;
            } else {
              getUserByUid(author_uid).then(data => {
                this.author = data;
              });
            }
          } else if (this.note.author.sid) {
            store.dispatch('user/loadCalnetUserByCsid', this.note.author.sid).then(data => {
              this.author = data;
            });
          } else {
            this.author = null;
          }
        }
      }
    }
  },
  methods:{
    getName: user => user.name || `${user.firstName} ${user.lastName}`
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
