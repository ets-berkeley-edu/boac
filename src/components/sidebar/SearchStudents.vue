<template>
  <div class="sidebar-section-search">
    <form id="search-students-form"
          v-bind:class="{'search-students-with-button': withButton}"
          v-on:submit.prevent="search()">
      <div class="search-students-form-label-outer" v-if="!withButton">
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
        <button id="search-students-button"
                class="btn btn-primary btn-search-students"
                type="submit">Search</button>
      </div>
    </form>
  </div>
</template>

<script>
import _ from 'lodash';
import router from '@/router';

export default {
  name: 'SearchStudents',
  data() {
    return {
      disable: false,
      searchPhrase: null,
      withButton: false
    };
  },
  methods: {
    search() {
      this.searchPhrase = _.trim(this.searchPhrase);
      if (this.searchPhrase) {
        router.push({ path: 'search', query: { q: this.searchPhrase } });
      }
    }
  }
};
</script>

<style scoped>
.sidebar-section-search {
  margin: 12px;
}
.search-students-form-button {
  min-width: 200px;
  width: 60%;
}
.search-students-form-label {
  font-weight: 400;
  margin: 0;
  padding-left: 3px;
}
.search-students-form-label-outer {
  color: #fff;
  margin: 10px 0;
}
.search-students-input {
  background-color: #fff;
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
</style>
