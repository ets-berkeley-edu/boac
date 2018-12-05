<template>
  <div class="cohort-container">
    <Spinner/>
    <CuratedGroupHeader v-if="!loading" :curatedGroup="curatedGroup"/>
    <hr class="filters-section-separator" v-if="!loading && !error && curatedGroup.students.length"/>
    <CuratedGroupList v-if="!loading" :curatedGroup="curatedGroup"/>
  </div>
</template>

<script>
import { getCuratedGroup } from '@/api/cohorts';
import Spinner from '@/components/Spinner.vue';
import Loading from '@/mixins/Loading.vue';
import CuratedGroupHeader from '@/components/curated/CuratedGroupHeader.vue';
import CuratedGroupList from '@/components/curated/CuratedGroupList.vue';

export default {
  name: 'CuratedGroup',
  mixins: [Loading],
  props: ['id'],
  components: {
    CuratedGroupHeader,
    CuratedGroupList,
    Spinner
  },
  data: () => ({
    curatedGroup: {},
    error: undefined
  }),
  created() {
    getCuratedGroup(this.id).then(data => {
      this.curatedGroup = data;
      this.loaded();
    });
  }
};
</script>

<style scoped>
</style>
