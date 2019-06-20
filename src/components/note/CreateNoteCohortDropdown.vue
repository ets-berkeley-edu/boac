<template>
  <div>
    <div>
      <label
        :for="`batch-note-${type}`"
        class="font-size-14 font-weight-bolder input-label text mt-2"><span class="sr-only">Select a </span>{{ header }}</label>
    </div>
    <b-dropdown
      :id="`batch-note-${type}`"
      :text="isCuratedGroupsMode ? 'Add Group' : 'Add Cohort'"
      :aria-label="`Note will be created for all students in selected ${type}${objects.length === 1 ? '' : 's'}`"
      variant="outline-dark"
      class="mb-2 ml-0 transparent">
      <b-dropdown-item
        v-for="object in objects"
        :key="object.id"
        :aria-label="`Add ${type} ${object.name}`"
        :disabled="includes(addedIds, object.id)"
        @click="addItem(object)">
        {{ truncate(object.name) }}
      </b-dropdown-item>
    </b-dropdown>
    <div>
      <div v-for="(addedObject, index) in added" :key="addedObject.id" class="mb-1">
        <span class="font-weight-bolder pill pill-attachment text-uppercase text-nowrap">
          {{ truncate(addedObject.name) }}
          <b-btn
            :id="`remove-${type}-from-batch-${index}`"
            :aria-label="`Remove ${type} ${addedObject.name}`"
            variant="link"
            class="p-0"
            @click.prevent="remove(addedObject)">
            <font-awesome icon="times-circle" class="font-size-24 has-error pl-2" />
          </b-btn>
        </span>
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
    addObject: Function,
    clearErrors: Function,
    objects: Array,
    isCuratedGroupsMode: Boolean,
    removeObject: Function
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
      this.addObject(object);
      this.alertScreenReader(`${this.type} '${object.name}' added`);
    },
    remove(object) {
      this.clearErrors();
      this.added = this.filterList(this.added, a => a.id !== object.id);
      this.removeObject(object);
      this.alertScreenReader(`${this.type} '${object.name}' removed`);
    }
  }
}
</script>
