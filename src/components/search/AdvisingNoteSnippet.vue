<template>
  <div
    :id="`advising-note-search-result-${note.id}`"
    class="advising-note-search-result"
    :class="{'demo-mode-blur': user.inDemoMode}">
    <h3 class="advising-note-search-result-header">
      <router-link
        :id="`advising-note-search-result-header-link-${note.id}`"
        class="advising-note-search-result-header-link"
        :class="{'demo-mode-blur': user.inDemoMode}"
        :to="`/student/${note.studentUid}#${note.id}`">
        {{ note.studentName }}
      </router-link>
      ({{ note.studentSid }})
    </h3>
    <div
      :id="`advising-note-search-result-snippet-${note.id}`"
      class="advising-note-search-result-snippet"
      v-html="note.noteSnippet">
    </div>
    <div class="advising-note-search-result-footer" :class="{'demo-mode-blur': user.inDemoMode}">
      <span v-if="note.advisorName" :id="`advising-note-search-result-advisor-${note.id}`">
        {{ note.advisorName }} -
      </span>
      <span v-if="lastModified">{{ lastModified | moment('MMM D, YYYY') }}</span>
    </div>
  </div>
</template>

<script>
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'AdvisingNoteSnippet',
  mixins: [UserMetadata, Util],
  props: {
    note: Object,
  },
  data: () => ({
    lastModified: undefined
  }),
  created() {
    const timestamp = this.get(this.note, 'updatedAt') || this.get(this.note, 'createdAt');
    if (timestamp) {
      const now = this.$moment();
      this.lastModified = this.$moment(timestamp).utcOffset(now.utcOffset());
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
