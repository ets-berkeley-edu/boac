<template>
  <div>
    <h2>CohortStudents</h2>
    <ul>
      <li v-for="student in students" :key="student.sid">
        {{ student }}
      </li>
    </ul>
  </div>
</template>

<script>
import CohortEditSession from '@/mixins/CohortEditSession';

export default {
  name: 'CohortStudents',
  mixins: [CohortEditSession]
};
</script>
