<template>
  <div
    :id="`advising-note-search-result-${note.id}`"
    :class="{'demo-mode-blur': currentUser.inDemoMode}"
    class="advising-note-search-result"
  >
    <h3 class="advising-note-search-result-header">
      <router-link
        v-if="note.studentUid"
        :id="`link-to-student-${note.studentUid}`"
        :class="{'demo-mode-blur': currentUser.inDemoMode}"
        :to="`${studentRoutePath(note.studentUid, currentUser.inDemoMode)}#note-${note.id}`"
        class="advising-note-search-result-header-link"
        v-html="note.studentName"
      />
      <span
        v-if="!note.studentUid"
        :id="`student-${note.studentSid}-has-no-uid`"
        class="font-weight-500"
        :class="{'demo-mode-blur': currentUser.inDemoMode}"
        v-html="note.studentName"
      />
      ({{ note.studentSid }})
    </h3>
    <div
      :id="`advising-note-search-result-snippet-${note.id}`"
      class="advising-note-search-result-snippet"
      v-html="note.noteSnippet"
    >
    </div>
    <div :class="{'demo-mode-blur': currentUser.inDemoMode}" class="advising-note-search-result-footer">
      <span v-if="note.advisorName" :id="`advising-note-search-result-advisor-${note.id}`">
        {{ note.advisorName }} -
      </span>
      <span v-if="lastModified">{{ $moment(lastModified).format('MMM D, YYYY') }}</span>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'

export default {
  name: 'AdvisingNoteSnippet',
  mixins: [Context, Util],
  props: {
    note: Object,
  },
  data: () => ({
    lastModified: undefined
  }),
  created() {
    const timestamp = this._get(this.note, 'updatedAt') || this._get(this.note, 'createdAt')
    if (timestamp) {
      this.lastModified = this.$moment(timestamp).tz(this.$config.timezone)
    }
  }
}
</script>
