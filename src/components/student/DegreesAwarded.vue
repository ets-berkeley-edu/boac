<template>
  <div v-if="_size(degreesAwarded)">
    <div
      v-for="(plans, dateAwarded) in degreesAwarded"
      :key="dateAwarded"
      class="student-text"
    >
      Graduated {{ moment(dateAwarded).format('MMM DD, YYYY') }} ({{ _join(plans, '; ') }})
    </div>
  </div>
</template>

<script>
import Util from '@/mixins/Util'

export default {
  name: 'DegreesAwarded',
  mixins: [Util],
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
    this._each(this.student.degrees || [], degree => {
      const key = degree.dateAwarded
      if (key) {
        const plans = this._filter(degree.plans || [], plan => {
          return this._includes(this.acceptedPlanTypes, plan.type)
        })
        if (plans.length) {
          this.degreesAwarded[key] = (this.degreesAwarded[key] || []).concat(this._map(plans, 'plan'))
        }
      }
    })
  }
}
</script>
