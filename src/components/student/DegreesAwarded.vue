<template>
  <div
    v-for="(plans, dateAwarded) in degreesAwarded"
    :key="dateAwarded"
    class="font-size-13 text-medium-emphasis"
  >
    Graduated {{ DateTime.fromSQL(dateAwarded).toLocaleString(DateTime.DATE_MED) }} ({{ join(plans, '; ') }})
  </div>
</template>

<script setup>
import {DateTime} from 'luxon'
import {each, filter, includes, join, map} from 'lodash'
import {onMounted, ref} from 'vue'

const props = defineProps({
  student: {
    required: true,
    type: Object
  }
})

const degreesAwarded = ref({})

onMounted(() => {
  each(props.student.degrees || [], degree => {
    const key = degree.dateAwarded
    if (key) {
      const plans = filter(degree.plans || [], plan => {
        return includes(['CRT', 'HS', 'MAJ', 'SP', 'SS'], plan.type)
      })
      if (plans.length) {
        degreesAwarded.value[key] = (degreesAwarded.value[key] || []).concat(map(plans, 'plan'))
      }
    }
  })
})
</script>
