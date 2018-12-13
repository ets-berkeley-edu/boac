<template>
  <div>
    <div tabindex="0" focus-on="renderPrimaryHeader">
      <div v-if="totalCourseCount">
        <h1 class="page-section-header">
          {{ 'class' | pluralize(totalCourseCount, {1: 'One'}, 'es') }} matching '{{ searchPhrase }}'
        </h1>
        <div v-if="courses.length < totalCourseCount">
          Showing the first {{courses.length}} classes.
        </div>
      </div>
    </div>
    <div class="sr-only"
         role="alert"
         v-if="totalCourseCount && coursesResorted">
      Courses sorted by {{ courseSortOptions.sortBy === 'section' ? 'section' : 'course name' }}
      {{ courseSortOptions.reverse ? 'descending' : 'ascending' }}
    </div>
    <table class="table-full-width" v-if="totalCourseCount">
      <tr>
        <th class="group-summary-column-header group-summary-header-sortable search-results-cell"
            @click="courseSort('section')"
            :class="{dropup: !courseSortOptions.reverse}"
            role="button"
            :aria-label="`Sort by section ${ courseSortOptions.sortBy === 'section' ? (courseSortOptions.reverse ? 'ascending' : 'descending') : ''}`">
          Section
          <span class="caret" v-if="courseSortOptions.sortBy === 'section'"></span>
        </th>
        <th class="group-summary-column-header group-summary-header-sortable search-results-cell"
            @click="courseSort('title')"
            :class="{dropup: !courseSortOptions.reverse}"
            role="button"
            :aria-label="`Sort by course name ${courseSortOptions.sortBy === 'title' ? (courseSortOptions.reverse ? 'ascending' : 'descending') : ''}`">
          Course Name
          <span class="caret" v-if="courseSortOptions.sortBy === 'title'"></span>
        </th>
        <th class="group-summary-column-header search-results-cell">
          Instructor(s)
        </th>
      </tr>
      <!--
      TODO: orderBy:'':courseSortOptions.reverse:courseComparator
      -->
      <tr v-for="course in courses" :key="course.id">
        <td class="search-results-cell">
          <span class="sr-only">Section</span>
          <router-link :to="{name: 'course', params: {termId: course.termId, sectionId: course.sectionId}}">
            {{ course.courseName }} - {{ course.instructionFormat }} {{ course.sectionNum }}
          </router-link>
        </td>
        <td class="search-results-cell">
          <span class="sr-only">Course Name</span>
          {{ course.courseTitle }}
        </td>
        <td :class="{'search-results-cell demo-mode-blur': user.inDemoMode, 'search-results-cell': !user.inDemoMode}">{{ course.instructors }}</td>
      </tr>
    </table>
  </div>
</template>

<script>
import UserMetadata from '@/mixins/UserMetadata';

export default {
  name: 'SortableCourseList',
  mixins: [UserMetadata],
  props: {
    searchPhrase: String,
    courses: Array,
    totalCourseCount: Number,
    renderPrimaryHeader: Boolean
  },
  data: () => ({
    coursesResorted: undefined,
    courseSortOptions: {
      sortBy: null,
      reverse: false
    }
  }),
  methods: {
    courseSort() {
      console.log('courseSort!!!');
    }
  }
};
</script>
