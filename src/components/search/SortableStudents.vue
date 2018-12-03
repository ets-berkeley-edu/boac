<template>
  <div v-if="students">
    <CuratedGroupSelector :students="students"/>
    <SortableStudentRow :student="student" v-for="student in students" v-bind:key="student.sid"/>
  </div>
</template>

<script>
import CuratedGroupSelector from '@/components/curated/CuratedGroupSelector';
import SortableStudentRow from '@/components/search/SortableStudentRow';

export default {
  name: 'SortableStudents',
  components: {
    CuratedGroupSelector,
    SortableStudentRow
  },
  props: {
    students: Array
  }
};
</script>
