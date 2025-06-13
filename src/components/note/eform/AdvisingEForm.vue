<template>
  <dl :id="`note-${note.id}-message-open`">
    <div v-if="note.eForm.dataSource === 'student_cpp_change_eforms'">
      <EFormCareerProgramPlanChange :e-form="note.eForm" :note-id="note.id" />
    </div>
    <div v-if="note.eForm.dataSource === 'student_course_load_eforms'">
      <EFormReducedCourseLoad :e-form="note.eForm" :note-id="note.id" />
    </div>
    <div v-if="note.eForm.dataSource === 'student_late_drop_eforms'">
      <EFormStudentLateDrop :e-form="note.eForm" />
    </div>
    <div class="mt-3">
      <dt class="font-weight-bold">Form ID</dt>
      <dd>{{ note.eForm.id }}</dd>
    </div>
    <div class="mt-3">
      <dt class="font-weight-bold">Date Initiated</dt>
      <dd>{{ DateTime.fromISO(note.createdAt).toFormat('MM/dd/yyyy') }}</dd>
    </div>
    <div class="mt-3">
      <dt class="font-weight-bold">Form Status </dt>
      <dd>{{ note.eForm.status }}</dd>
    </div>
    <div v-if="note.eForm.dataSource === 'student_late_drop_eforms'" class="mt-3">
      <dt class="font-weight-bold">Final Date &amp; Time Stamp</dt>
      <dd>{{ DateTime.fromISO(note.updatedAt).toFormat('MM/dd/yyyy h:mm:ssa') }}</dd>
    </div>
    <div v-if="note.eForm.dataSource !== 'student_late_drop_eforms'" class="mt-3">
      <dt class="font-weight-bold">Last Updated</dt>
      <dd>{{ DateTime.fromISO(note.updatedAt).toFormat('MM/dd/yyyy') }}</dd>
    </div>
  </dl>
</template>

<script setup lang="ts">
import {DateTime} from 'luxon'
import EFormCareerProgramPlanChange from '@/components/note/eform/EFormCareerProgramPlanChange.vue'
import EFormStudentLateDrop from '@/components/note/eform/EFormStudentLateDrop.vue'
import EFormReducedCourseLoad from '@/components/note/eform/EFormReducedCourseLoad.vue'

defineProps({
  note: {
    required: true,
    type: Object
  }
})
</script>
