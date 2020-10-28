<template>
  <div>
    <b-button
      :id="`add-student-${student.sid}-to-group`"
      class="font-size-14 p-0"
      variant="link"
      @click="openMenu"
    >
      Add to Group
    </b-button>
  </div>
</template>

<script>
export default {
  name: 'CuratedStudentSelector',
  props: {
    student: {
      required: true,
      type: Object
    }
  },
  methods: {
    openMenu() {
      // TODO
    }
  }
}
</script>
