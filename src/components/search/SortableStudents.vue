<template>
  <ul>
    <li v-for="student in students" v-bind:key="student.sid">
      <StudentAvatar v-bind:student="student"/>
      {{ student.sid }}
    </li>
  </ul>
</template>

<script>
import StudentAvatar from '@/components/student/StudentAvatar';

export default {
  name: 'SortableStudents',
  components: {
    StudentAvatar
  },
  props: ['students']
};
</script>

<style scoped>
</style>
