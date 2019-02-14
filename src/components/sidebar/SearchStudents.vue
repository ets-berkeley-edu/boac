<template>
  <div class="sidebar-section-search">
    <form
      id="search-students-form"
      autocomplete="off"
      :class="{'search-students-with-button': withButton}"
      @submit.prevent="search()">
      <div v-if="!withButton" class="search-students-form-label-outer search-label">
        <i class="fas fa-search"></i>
        <label
          for="search-students-input"
          class="search-students-form-label">Search Students or Classes</label>
      </div>
      <div :class="{'search-students-form-button': withButton}">
        <input
          id="search-students-input"
          v-model="searchPhrase"
          class="search-students-input"
          :readonly="disable"
          type="text"
          maxlength="255" />
      </div>
      <div v-if="withButton">
        <b-btn
          id="search-students-button"
          variant="primary"
          class="btn-search-students btn-primary-color-override"
          type="submit">
          Search
        </b-btn>
      </div>
    </form>
  </div>
</template>

<script>
import GoogleAnalytics from '@/mixins/GoogleAnalytics';
import Util from '@/mixins/Util';

export default {
  name: 'SearchStudents',
  mixins: [GoogleAnalytics, Util],
  props: {
    includeCourses: {
      default: false,
      type: Boolean
    },
    withButton: Boolean
  },
  data() {
    return {
      disable: false,
      searchPhrase: null
    };
  },
  methods: {
    search() {
      this.searchPhrase = this.trim(this.searchPhrase);
      if (this.searchPhrase) {
        this.$router.push({
          path: this.forceUniquePath('/search'),
          query: {
            q: this.searchPhrase,
            includeCourses: this.includeCourses
          }
        });
        this.gaEvent(
          'Search',
          'submit',
          this.includeCourses ? 'classes and students' : 'students',
          this.searchPhrase
        );
      }
    }
  }
};
</script>

<style scoped>
.btn-search-students {
  height: 46px;
}
.search-label {
  display: flex;
  align-items: baseline;
  font-size: 14px;
}
.search-label i {
  padding-right: 4px;
}
.search-students-form-button {
  min-width: 200px;
  width: 60%;
}
.search-students-form-label {
  font-weight: 400;
  margin: 0;
}
.search-students-form-label-outer {
  color: #fff;
  margin: 10px 0;
}
.search-students-input {
  box-sizing: border-box;
  border: 2px solid #ccc;
  border-radius: 4px;
  color: #333;
  padding: 10px;
  width: 100%;
}
.search-students-with-button {
  align-items: center;
  display: flex;
  flex-flow: row wrap;
  margin-top: 10px;
}
.search-students-with-button div {
  align-self: flex-end;
}
.search-students-with-button div:first-child {
  padding-right: 15px;
}
.sidebar-section-search {
  margin: 0 12px 12px 12px;
}
</style>
