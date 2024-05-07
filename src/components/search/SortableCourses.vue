<template>
  <div>
    <table class="table-full-width">
      <tr>
        <th>
          <button
            id="column-sort-button-section"
            class="btn btn-link table-header-text cursor-pointer table-cell"
            @click="courseSort('section')"
            @keyup.enter="courseSort('section')"
          >
            Section
            <span v-if="sort.by === 'section'">
              <v-icon :icon="sort.reverse.section ? mdiMenuDown : mdiMenuUp" />
            </span>
          </button>
        </th>
        <th>
          <button
            id="column-sort-button-title"
            class="btn btn-link table-header-text cursor-pointer table-cell"
            @click="courseSort('title')"
            @keyup.enter="courseSort('title')"
          >
            Course Name
            <span v-if="sort.by === 'title'">
              <v-icon :icon="sort.reverse.title ? mdiMenuDown : mdiMenuUp" />
            </span>
          </button>
        </th>
        <th class="table-cell">
          <span class="table-header-text">Instructor(s)</span>
        </th>
      </tr>
      <tr v-for="course in sortedCourses" :key="course.id">
        <td class="table-cell">
          <span class="sr-only">Section</span>
          <router-link :to="`/course/${course.termId}/${course.sectionId}`">
            {{ course.courseName }} - {{ course.instructionFormat }} {{ course.sectionNum }}
          </router-link>
        </td>
        <td class="table-cell">
          <span class="sr-only">Course Name</span>
          {{ course.courseTitle }}
        </td>
        <td class="table-cell">{{ course.instructors }}</td>
      </tr>
    </table>
  </div>
</template>

<script setup>
import {mdiMenuDown, mdiMenuUp} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import {alertScreenReader} from '@/lib/utils'

export default {
  name: 'SortableCourses',
  mixins: [Context, Util],
  props: {
    courses: {
      required: true,
      type: Array
    }
  },
  data: () => ({
    sort: {
      by: null,
      reverse: {
        section: false,
        title: false
      }
    },
    sortedCourses: []
  }),
  created() {
    this.sort.by = 'section'
    // TODO: do not mutate prop
    this.sortedCourses = this.courses.sort(this.courseComparator) // eslint-disable-line vue/no-mutating-props
  },
  methods: {
    courseSort(sortBy) {
      if (this.sort.by !== sortBy) {
        this.sort.by = sortBy
        this.sort.reverse[sortBy] = false
        // TODO: do not mutate prop
        this.sortedCourses = this.courses.sort(this.courseComparator) // eslint-disable-line vue/no-mutating-props
      } else {
        this.sort.reverse[sortBy] = !this.sort.reverse[sortBy]
        this.sortedCourses = this.sortedCourses.reverse()
      }
      alertScreenReader(`Courses sorted by ${this.sort.by === 'section' ? 'section' : 'course name'} ${this.describeReverse(this.sort.reverse[this.sort.by])}`)
    },
    courseComparator(c1, c2) {
      if (this.sort.by === 'title' && c1.courseTitle !== c2.courseTitle) {
        return c1.courseTitle > c2.courseTitle ? 1 : -1
      }
      // If sorting by section name, attempt to compare by subject area.
      let split1 = this.splitCourseName(c1)
      let split2 = this.splitCourseName(c2)
      if (split1[0] > split2[0]) {
        return 1
      }
      if (split1[0] < split2[0]) {
        return -1
      }
      // If subject areas are identical, extract and compare numeric portion of catalog id.
      let code1 = parseInt(split1[1].match(/\d+/)[0], 10)
      let code2 = parseInt(split2[1].match(/\d+/)[0], 10)
      if (code1 > code2) {
        return 1
      }
      if (code1 < code2) {
        return -1
      }
      // If catalog ids are numerically identical then handle prefixes and suffixes with alphabetic comparison.
      if (split1[1] > split2[1]) {
        return 1
      }
      if (split1[1] < split2[1]) {
        return -1
      }
      // Instruction format and section number.
      if (c1.instructionFormat > c2.instructionFormat) {
        return 1
      }
      if (c1.instructionFormat < c2.instructionFormat) {
        return -1
      }
      return c1.sectionNum > c2.sectionNum ? 1 : -1
    },
    splitCourseName(course) {
      let split = course.courseName.split(' ')
      return [split.slice(0, -1).join(' '), split[split.length - 1]]
    },
    describeReverse: reverse => (reverse ? 'descending' : '')
  }
}
</script>

<style scoped>
.table-cell {
  padding: 5px 10px 5px 0;
  vertical-align: top;
  width: 33%;
}
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
