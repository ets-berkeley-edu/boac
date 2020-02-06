<template>
  <div>
    {{ student }}
  </div>
</template>

<script>
export default {
  name: 'AdmitStudentRow',
  props: {
    rowIndex: {
      required: true,
      type: Number
    },
    sortedBy: {
      required: true,
      type: String
    },
    student: {
      required: true,
      type: Object
    }
  },
}
</script>
