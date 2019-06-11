<template>
  <div>
    <div>
      <label :for="`batch-note-${type}`" class="input-label mb-1">{{ header }}</label>
    </div>
    <b-dropdown :id="`batch-note-${type}`" :text="isCuratedGroupsMode ? 'Add Group' : 'Add Cohort'" class="m-md-2">
      <b-dropdown-item
        v-for="object in objects"
        :key="object.id"
        :disabled="includes(addedIds, object.id)"
        @click="addItem(object)">
        {{ truncate(object.name) }}
      </b-dropdown-item>
    </b-dropdown>
    <div>
      <div v-for="(addedObject, index) in added" :key="addedObject.id">
        {{ addedObject.name }}
        <b-btn
          :id="`remove-${type}-from-batch-${index}`"
          variant="link"
          class="p-0"
          @click.prevent="removeObject(addedObject)">
          <i class="fas fa-times-circle has-error pl-2"></i>
          <span class="sr-only">Remove {{ type }} {{ addedObject.name }} from note creation</span>
        </b-btn>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'CreateNoteCohortDropdown',
  mixins: [Context, UserMetadata, Util],
  props: {
    addObjectId: Function,
    clearErrors: Function,
    objects: Array,
    isCuratedGroupsMode: Boolean,
    removeObjectId: Function
  },
  data: () => ({
    added: [],
    header: undefined,
    type: undefined
  }),
  computed: {
    addedIds() {
      return this.map(this.added, 'id');
    }
  },
  created() {
    this.header = this.isCuratedGroupsMode ? 'Curated Group' : 'Cohort';
    this.objects = this.isCuratedGroupsMode ? this.myCuratedGroups : this.myCohorts;
    this.type = this.isCuratedGroupsMode ? 'curated' : 'cohort';
  },
  methods: {
    addItem(object) {
      this.clearErrors();
      this.added.push(object);
      this.addObjectId(object.id);
      this.alertScreenReader(`${this.type} '${object.name}' added`);
    },
    removeObject(object) {
      this.clearErrors();
      this.added = this.filterList(this.added, a => a.id !== object.id);
      this.removeObjectId(object.id);
      this.alertScreenReader(`${this.type} '${object.name}' removed`);
    }
  }
}
</script>

<style scoped>

</style>
