<template>
  <div class="cohort-container">
    <Spinner/>
    <CuratedGroupHeader v-if="!loading" :curatedGroup="curatedGroup"/>
    <hr class="filters-section-separator" v-if="!loading && !error && curatedGroup.students.length"/>
    <Students v-if="!loading"
              :listName="curatedGroup.name"
              listType="curatedGroup"
              :students="curatedGroup.students"/>
  </div>
</template>

<script>
import CuratedGroupHeader from '@/components/curated/CuratedGroupHeader';
import Loading from '@/mixins/Loading';
import router from '@/router';
import Spinner from '@/components/util/Spinner';
import store from '@/store';
import Students from '@/components/student/Students';
import { getCuratedGroup, removeFromCuratedGroup } from '@/api/curated';

export default {
  name: 'CuratedGroup',
  mixins: [Loading],
  props: ['id'],
  components: {
    CuratedGroupHeader,
    Spinner,
    Students
  },
  data: () => ({
    curatedGroup: {},
    error: undefined
  }),
  created() {
    getCuratedGroup(this.id).then(data => {
      if (data) {
        this.curatedGroup = data;
        this.loaded();
        document.title = `${this.curatedGroup.name} | BOAC`;
      } else {
        router.push({ path: '/404' });
      }
    });
    this.$eventHub.$on('curated-group-remove-student', sid =>
      this.$_Students_removeStudent(sid)
    );
  },
  methods: {
    $_Students_removeStudent: function(sid) {
      removeFromCuratedGroup(this.curatedGroup.id, sid).then(() => {
        let deleteIndex = this.curatedGroup.students.findIndex(student => {
          return student.sid === sid;
        });
        this.curatedGroup.students.splice(deleteIndex, 1);
        this.curatedGroup.studentCount = this.curatedGroup.students.length;
        store.commit('curated/updateCuratedGroup', this.curatedGroup);
      });
    }
  }
};
</script>
