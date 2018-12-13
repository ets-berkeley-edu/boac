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
         v-if="totalCourseCount && resorted">
      Courses sorted by {{ sort.by === 'section' ? 'section' : 'course name' }} {{ describeReverse(sort.reverse.section) }}
    </div>
    <table class="table-full-width" v-if="totalCourseCount">
      <tr role="row">
        <th :class="{ dropup: !sort.reverse.section }">
          <button id="column-sort-button-section"
                  class="btn btn-link table-header-text group-summary-column-header group-summary-header-sortable search-results-cell"
                  :aria-label="`Sort by section ${ sort.by === 'section' ? describeReverse(sort.reverse.section) : ''}`"
                  tabindex="0"
                  @click="courseSort('section')">
            Section
            <span class="caret" v-if="sort.by === 'section'">
              <i :class="{
                'fas fa-caret-down': sort.reverse.section,
                'fas fa-caret-up': !sort.reverse.section
              }"></i>
            </span>
          </button>
        </th>
        <th :class="{ dropup: !sort.reverse.title }">
          <button id="column-sort-button-title"
                  class="btn btn-link table-header-text group-summary-column-header group-summary-header-sortable search-results-cell"
                  :aria-label="`Sort by course name ${ sort.by === 'title' ? describeReverse(sort.reverse.title) : ''}`"
                  tabindex="0"
                  @click="courseSort('title')">
            Course Name
            <span class="caret" v-if="sort.by === 'title'">
              <i :class="{
                'fas fa-caret-down': sort.reverse.title,
                'fas fa-caret-up': !sort.reverse.title
              }"></i>
            </span>
          </button>
        </th>
        <th class="group-summary-column-header search-results-cell">
          <span class="table-header-text">Instructor(s)</span>
        </th>
      </tr>
      <tr v-for="course in courses" :key="course.id">
        <td class="search-results-cell">
          <span class="sr-only">Section</span>
          <router-link :to="`/course/${course.termId}/${course.sectionId}`">
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
    resorted: undefined,
    sort: {
      by: null,
      reverse: {
        section: false,
        title: false
      }
    }
  }),
  created() {
    this.courseSort('section');
  },
  methods: {
    courseSort(sortBy) {
      this.sort.reverse[sortBy] = !this.sort.reverse[sortBy];
      if (this.sort.by !== sortBy) {
        this.sort.by = sortBy;
        this.courses = this.courses.sort(this.courseComparator);
      }
      this.courses = this.courses.reverse();
      this.resorted = true;
    },
    courseComparator(c1, c2) {
      if (this.sort.by === 'title' && c1.courseTitle !== c2.courseTitle) {
        return c1.courseTitle > c2.courseTitle ? 1 : -1;
      }
      // If sorting by section name, attempt to compare by subject area.
      let split1 = this.splitCourseName(c1);
      let split2 = this.splitCourseName(c2);
      if (split1[0] > split2[0]) {
        return 1;
      }
      if (split1[0] < split2[0]) {
        return -1;
      }
      // If subject areas are identical, extract and compare numeric portion of catalog id.
      let code1 = parseInt(split1[1].match(/\d+/)[0], 10);
      let code2 = parseInt(split2[1].match(/\d+/)[0], 10);
      if (code1 > code2) {
        return 1;
      }
      if (code1 < code2) {
        return -1;
      }
      // If catalog ids are numerically identical then handle prefixes and suffixes with alphabetic comparison.
      if (split1[1] > split2[1]) {
        return 1;
      }
      if (split1[1] < split2[1]) {
        return -1;
      }
      // Instruction format and section number.
      if (c1.instructionFormat > c2.instructionFormat) {
        return 1;
      }
      if (c1.instructionFormat < c2.instructionFormat) {
        return -1;
      }
      return c1.sectionNum > c2.sectionNum ? 1 : -1;
    },
    splitCourseName(course) {
      let split = course.courseName.split(' ');
      return [split.slice(0, -1).join(' '), split[split.length - 1]];
    },
    describeReverse: reverse => (reverse ? 'descending' : 'ascending')
  }
};
</script>

<style scoped>
.table-header-text {
  color: #999 !important;
  font-size: 12px;
  font-weight: bold;
  padding: 0;
  text-decoration: none;
  width: fit-content;
}
.table-header-text:focus {
  outline: -webkit-focus-ring-color auto 5px;
}
</style>
