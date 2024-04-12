<template>
  <div
    v-for="(plans, dateAwarded) in degreesAwarded"
    :key="dateAwarded"
    class="student-text"
  >
    Graduated {{ DateTime.fromSQL(dateAwarded).toLocaleString(DateTime.DATE_MED) }} ({{ join(plans, '; ') }})
  </div>
</template>

<script setup>
import {DateTime} from 'luxon'
import {each, filter, includes, join, map} from 'lodash'
</script>

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
    degreesAwarded: {}
  }),
  created() {
    each(this.student.degrees || [], degree => {
      const key = degree.dateAwarded
      if (key) {
        const plans = filter(degree.plans || [], plan => {
          return includes(this.acceptedPlanTypes, plan.type)
        })
        if (plans.length) {
          this.degreesAwarded[key] = (this.degreesAwarded[key] || []).concat(map(plans, 'plan'))
        }
      }
    })
  }
}
</script>
