<template>
  <div class="pl-3 pt-3">
    <h1>Bulk Add Students</h1>
    <div v-if="curatedGroup">
      Add students to "<strong>{{ curatedGroup.name }}</strong>" by adding their Student Identification (SID) numbers below.
    </div>
    <div v-if="!curatedGroup">
      Create a curated group of students by adding their Student Identification (SID) numbers below.
    </div>
    <div v-if="error">
      {{ error }}
    </div>
    <div>
      <b-form-textarea
        id="curated-group-bulk-add-sids"
        v-model="sids"
        placeholder="Type or paste a list of SID numbers. Example: 3033223869, 3033112579"
        rows="3"
        max-rows="30"
        @change="clearError"
      ></b-form-textarea>
    </div>
    <div>
      <b-btn
        id="btn-curated-group-bulk-add-sids"
        class="pl-2"
        variant="primary"
        @click.stop="submitSids">
        Next
      </b-btn>
    </div>
  </div>
</template>

<script>
import Loading from '@/mixins/Loading';
import Util from '@/mixins/Util';
import { getCuratedGroup } from '@/api/curated';
import { validateSids } from '@/api/student';

export default {
  name: 'CuratedGroupBulkAdd',
  mixins: [Loading, Util],
  data: () => ({
    curatedGroup: undefined,
    error: undefined,
    sids: undefined
  }),
  mounted() {
    const id = this.toInt(this.get(this.$route, 'params.id'));
    if (id) {
      getCuratedGroup(id).then(data => {
        if (data) {
          this.curatedGroup = data;
          this.setPageTitle(this.curatedGroup.name);
          this.loaded();
        } else {
          this.$router.push({ path: '/404' });
        }
      });
    } else {
      this.loaded();
    }
  },
  methods: {
    clearError() {
      this.error = null;
    },
    submitSids() {
      const trimmed = this.trim(this.sids);
      if (trimmed) {
        const split = this.split(trimmed, ',');
        const notNumeric = this.partition(split, sid => this.toInt(sid))[1];
        if (notNumeric.length) {
          this.error = `Please fix the invalid entries: ${notNumeric}`;
        } else {
          validateSids(split).then(data => {
            const valid = [];
            const unavailable = [];
            const notFound = [];
            this.each(data, entry => {
              switch(entry.status) {
                case 200:
                  valid.push(entry.sid);
                  break;
                case 401:
                  unavailable.push(entry.sid);
                  break;
                default:
                  notFound.push(entry.sid);
              }
            });
            if (notFound) {
              const count = this.size(notFound);
              const pluralize = count === 1 ? '1 student' : `${count} students`;
              this.error = `Uh oh! ${pluralize} not found: ${notFound.join(', ')}`;
            }
          });
        }
      } else {
        this.error = 'Please provide one or more SIDs.';
      }
    }
  }
}
</script>

<style scoped>

</style>
