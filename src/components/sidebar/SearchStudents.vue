<template>
  <div class="sidebar-section-search">
    <form id="search-students-form"
          v-bind:class="{'search-students-with-button': withButton}"
          v-on:submit.prevent="search()">
      <div class="search-students-form-label-outer search-label" v-if="!withButton">
        <i class="fas fa-search"></i>
        <label for="search-students-input"
               class="search-students-form-label">Search Students or Classes</label>
      </div>
      <div v-bind:class="{'search-students-form-button': withButton}">
        <input id="search-students-input"
               type="text"
               class="search-students-input"
               v-model="searchPhrase"
               :readonly="disable"
               maxlength="255"/>
      </div>
      <div v-if="withButton">
        <b-btn id="search-students-button"
               variant="primary"
               class="btn-search-students btn-primary-color-override"
               type="submit">Search</b-btn>
      </div>
    </form>
  </div>
</template>

<script>
import Util from '@/mixins/Util';

export default {
  name: 'SearchStudents',
  mixins: [Util],
  props: {
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
            includeCourses: 'true'
          }
        });
      }
    }
  }
};
</script>

<style scoped>
.search-label {
  display: flex;
  align-items: baseline;
  font-size: 14px;
}
.search-label i {
  padding-right: 4px;
}
</style>
