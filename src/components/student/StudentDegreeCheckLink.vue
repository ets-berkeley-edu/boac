<template>
  <v-btn
    v-if="currentUser.canReadDegreeProgress"
    :id="`degree-checks-of-${student.sid}`"
    class="font-size-13 font-weight-medium letter-spacing-normal"
    color="primary"
    href="#"
    role="link"
    tag="a"
    variant="text"
    @click="() => goToStudentDegreeChecks(student.sid)"
  >
    <div class="align-center d-flex text-anchor">
      <div>
        Undergraduate Degree Checks <span class="sr-only">of {{ student.name }} (opens in new tab)</span>
      </div>
      <v-icon class="ml-1" :icon="mdiOpenInNew" size="14" />
    </div>
  </v-btn>
</template>

<script setup>
import {mdiOpenInNew} from '@mdi/js'
import {goToStudentDegreeChecks} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

defineProps({
  student: {
    required: true,
    type: Object
  }
})

const currentUser = useContextStore().currentUser
</script>
