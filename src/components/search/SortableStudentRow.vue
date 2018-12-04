<template>
  <div>
    <CuratedStudentCheckbox :sid="student.sid"/>
    <StudentAvatar :student="student" size="small"/>
    {{ student.name }}
  </div>
</template>

<script>
import CuratedStudentCheckbox from '@/components/curated/CuratedStudentCheckbox';
import StudentAvatar from '@/components/student/StudentAvatar';

export default {
  name: 'SortableStudentRow',
  components: {
    CuratedStudentCheckbox,
    StudentAvatar
  },
  props: {
    student: Object
  }
};
</script>
