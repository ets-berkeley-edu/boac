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
    acceptedPlanTypes: ['CRT', 'HS', 'MAJ', 'SP', 'SS'],
    degreesAwarded: undefined
  }),
  created() {
    this.degreesAwarded = {}
    this.$_.each(this.student.degrees || [], degree => {
      const key = degree.dateAwarded
      if (key) {
        const plans = this.$_.filter(degree.plans || [], plan => {
          return this.$_.includes(this.acceptedPlanTypes, plan.type)
        })
        if (plans.length) {
          this.degreesAwarded[key] = (this.degreesAwarded[key] || []).concat(this.$_.map(plans, 'plan'))
        }
      }
    })
  }
}
</script>
