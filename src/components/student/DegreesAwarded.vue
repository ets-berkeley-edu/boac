<template>
  <div v-if="$_.size(degreesAwarded)">
    <div
      v-for="(plans, dateAwarded) in degreesAwarded"
      :key="dateAwarded"
      class="student-text"
    >
      Graduated {{ dateAwarded | moment('MMM DD, YYYY') }} ({{ $_.join(plans, '; ') }})
    </div>
  </div>
</template>

<script>
export default {
  name: 'DegreesAwarded',
  props: {
    student: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    degreesAwarded: undefined
  }),
  created() {
    this.degreesAwarded = {}
    this.$_.each(this.student.degrees || [], degree => {
      const key = degree.dateAwarded
      if (key) {
        const plans = this.degreesAwarded[key] || []
        this.degreesAwarded[key] = plans.concat(this.$_.map(degree.plans, 'plan'))
      }
    })
  }
}
</script>
