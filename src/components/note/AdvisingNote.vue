<template>
  <div>
    <div :id="`note-${note.id}-message-closed`" :class="{'truncate': !isOpen}">
      <span v-if="note.subject">{{ note.subject }}</span>
      <span v-if="!note.subject && size(note.message)" v-html="note.message"></span>
      <span v-if="!note.subject && !size(note.message)">{{ note.category }}<span v-if="note.subcategory">, {{ note.subcategory }}</span></span>
    </div>
    <div v-if="isOpen && note.subject && note.message" class="mt-2">
      <span :id="`note-${note.id}-message-open`" v-html="note.message"></span>
    </div>
    <div v-if="!isUndefined(author) && !author.name" class="mt-2 advisor-profile-not-found">
      Advisor profile not found
    </div>
    <div v-if="author" class="mt-2">
      <div v-if="author.name">
        <a
          :id="`note-${note.id}-author-name`"
          :aria-label="`Open UC Berkeley Directory page of ${author.name} in a new window`"
          :href="`https://www.berkeley.edu/directory/results?search-term=${author.name}`"
          target="_blank">{{ author.name }}</a>
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
      <div class="pill-list-header mt-3 mb-1">{{ size(note.topics) === 1 ? 'Topic Category' : 'Topic Categories' }}</div>
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
      <div v-if="isPreCsNote" class="faint-text">
        Pre-Fall 2016 attachment<span v-if="size(note.attachments) > 1">s</span> unavailable
      </div>
      <ul class="pill-list pl-0">
        <li
          v-for="(attachment, index) in note.attachments"
          :key="attachment.sisFilename"
          class="mt-2"
          @click.stop>
          <a
            v-if="!isPreCsNote"
            :id="`note-${note.id}-attachment-${index}`"
            :href="downloadUrl(attachment)"
            class="pill text-nowrap">
            <i class="fas fa-paperclip"></i> {{ attachment.userFilename || attachment.sisFilename }}
          </a>
          <span
            v-if="isPreCsNote"
            :id="`note-${note.id}-attachment-${index}`"
            class="pill text-nowrap"><i class="fas fa-paperclip"></i> {{ attachment.userFilename || attachment.sisFilename }}
          </span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import store from '@/store'
import Context from '@/mixins/Context';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { getUserByUid } from '@/api/user';

export default {
  name: 'AdvisingNote',
  mixins: [Context, UserMetadata, Util],
  props: {
    isOpen: Boolean,
    note: Object
  },
  data: () => ({
    allUsers: undefined,
    author: undefined
  }),
  computed: {
    isPreCsNote() {
      return this.get(this.note, 'createdBy') === 'UCBCONVERSION';
    }
  },
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
  methods: {
    downloadUrl(attachment) {
      return this.apiBaseUrl + '/api/notes/attachment/' + attachment.sisFilename;
    }
  },
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
.advisor-profile-not-found {
  color: #999;
  font-size: 14px;
}
</style>
