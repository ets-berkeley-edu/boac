<template>
  <div
    :id="`advising-note-search-result-${note.id}`"
    class="advising-note-search-result"
    :class="{'demo-mode-blur': get(user, 'inDemoMode', true)}">
    <h3 class="advising-note-search-result-header">
      <router-link
        :id="`advising-note-search-result-header-link-${note.id}`"
        class="advising-note-search-result-header-link"
        :class="{'demo-mode-blur': get(user, 'inDemoMode', true)}"
        :to="`/student/${note.studentUid}`">
        {{ note.studentName }}
      </router-link>
      ({{ note.studentSid }})
    </h3>
    <div
      :id="`advising-note-search-result-snippet-${note.id}`"
      class="advising-note-search-result-snippet"
      v-html="note.noteSnippet">
    </div>
    <div class="advising-note-search-result-footer" :class="{'demo-mode-blur': get(user, 'inDemoMode', true)}">
      <span v-if="note.advisorName" :id="`advising-note-search-result-advisor-${note.id}`">
        {{ note.advisorName }} -
      </span>
      {{ note.lastModified }}
    </div>
  </div>
</template>

<script>
import { format as formatDate, parse as parseDate } from 'date-fns';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'AdvisingNoteSnippet',
  mixins: [UserMetadata, Util],
  props: {
    note: Object,
  },
  created() {
    const timestamp = this.get(this.note, 'updatedAt') || this.get(this.note, 'createdAt')
    if (timestamp) {
      const d = parseDate(timestamp);
      this.note.lastModified = formatDate(d, 'MMM DD, YYYY');
    }
  }
};
</script>

<style>
.advising-note-search-result {
  margin: 15px 0;
}
.advising-note-search-result-header {
  font-weight: 400;
  font-size: 18px;
  margin-bottom: 5px;
}
.advising-note-search-result-header-link {
   font-weight: 600;
}
.advising-note-search-result-footer {
  color: #999;
  font-size: 14px;
}
.advising-note-search-result-snippet {
  font-size: 16px;
  line-height: 1.3em;
  margin: 5px 0;
}
</style>
