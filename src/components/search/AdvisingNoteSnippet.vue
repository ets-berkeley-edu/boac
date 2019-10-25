<template>
  <div
    :id="`advising-note-search-result-${note.id}`"
    :class="{'demo-mode-blur': user.inDemoMode}"
    class="advising-note-search-result">
    <h3 class="advising-note-search-result-header">
      <router-link
        :id="`link-to-student-${note.studentUid}`"
        :class="{'demo-mode-blur': user.inDemoMode}"
        :to="`${studentRoutePath(note.studentUid, user.inDemoMode)}#note-${note.id}`"
        v-html="note.studentName"
        class="advising-note-search-result-header-link"></router-link>
      ({{ note.studentSid }})
    </h3>
    <div
      :id="`advising-note-search-result-snippet-${note.id}`"
      v-html="note.noteSnippet"
      class="advising-note-search-result-snippet">
    </div>
    <div :class="{'demo-mode-blur': user.inDemoMode}" class="advising-note-search-result-footer">
      <span v-if="note.advisorName" :id="`advising-note-search-result-advisor-${note.id}`">
        {{ note.advisorName }} -
      </span>
      <span v-if="lastModified">{{ lastModified | moment('MMM D, YYYY') }}</span>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'AdvisingNoteSnippet',
  mixins: [Context, UserMetadata, Util],
  props: {
    note: Object,
  },
  data: () => ({
    lastModified: undefined
  }),
  created() {
    const timestamp = this.get(this.note, 'updatedAt') || this.get(this.note, 'createdAt');
    if (timestamp) {
      this.lastModified = this.$moment(timestamp).tz(this.timezone);
    }
  }
};
</script>
