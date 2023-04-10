<template>
  <div>
    Bonjour le monde!
  </div>
</template>

<script>
import Scrollable from '@/mixins/Scrollable.vue'
export default {
  name: 'DraftNotes',
  mixins: [Scrollable],
  created() {
    this.scrollToTop()
  }
}
</script>
