<template>
  <div v-if="formattedDate">
    <span class="sr-only">{{ srPrefix }} </span>{{ formattedDate }}
    <div v-if="timeOfDay">
      {{ timeOfDay }}
    </div>
  </div>
</template>

<script>
import { format as formatDate, parse as parseDate } from 'date-fns';

export default {
  name: 'TimelineDate',
  props: {
    date: String,
    includeTimeOfDay: Boolean,
    srPrefix: String
  },
  data: () => ({
    formattedDate: undefined,
    now: new Date(),
    timeOfDay: undefined
  }),
  created() {
    if (this.date) {
      const d = parseDate(this.date);
      const dateFormat =
        d.getFullYear() === this.now.getFullYear()
          ? 'MMM DD'
          : 'MMM DD, YYYY';
      this.formattedDate = formatDate(d, dateFormat);
      if (this.includeTimeOfDay) {
        this.timeOfDay = formatDate(d, 'H:mma')
      }
    }
  }
}
</script>
