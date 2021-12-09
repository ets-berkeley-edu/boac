<template>
  <div>
    <div>
      <label
        :for="`batch-note-${type}`"
        class="font-size-14 font-weight-bolder input-label text mt-2"
      ><span class="sr-only">Select a </span>{{ header }}</label>
    </div>
    <b-dropdown
      :id="`batch-note-${type}`"
      :disabled="disabled"
      :text="isCuratedGroupsMode ? 'Add Group' : 'Add Cohort'"
      :aria-label="`Note will be created for all students in selected ${type}${objects.length === 1 ? '' : 's'}`"
      variant="outline-dark"
      class="mb-2 ml-0 transparent"
    >
      <b-dropdown-item
        v-for="object in objects"
        :id="`batch-note-${type}-option-${object.id}`"
        :key="object.id"
        :aria-label="`Add ${type} ${object.name}`"
        :disabled="$_.includes(addedIds, object.id)"
        @click="addItem(object)"
      >
        {{ $_.truncate(object.name) }}
      </b-dropdown-item>
    </b-dropdown>
    <div>
      <div v-for="(addedObject, index) in added" :key="addedObject.id" class="mb-1">
        <span class="font-weight-bolder pill pill-attachment text-uppercase text-nowrap">
          <span :id="`batch-note-${type}-${index}`">{{ $_.truncate(addedObject.name) }}</span>
          <b-btn
            :id="`remove-${type}-from-batch-${index}`"
            variant="link"
            class="p-0"
            @click.prevent="remove(addedObject)"
          >
            <font-awesome icon="times-circle" class="font-size-24 has-error pl-2" />
            <span class="sr-only">Remove</span>
          </b-btn>
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'

export default {
  name: 'BatchNoteAddCohort',
  mixins: [Context, Util],
  props: {
    addObject: {
      required: true,
      type: Function
    },
    disabled: {
      required: false,
      type: Boolean
    },
    objects: {
      required: true,
      type: Array
    },
    isCuratedGroupsMode: {
      required: true,
      type: Boolean
    },
    removeObject: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    added: [],
    header: undefined,
    type: undefined
  }),
  computed: {
    addedIds() {
      return this.$_.map(this.added, 'id')
    }
  },
  created() {
    this.header = this.isCuratedGroupsMode ? 'Curated Group' : 'Cohort'
    // TODO: do not mutate prop
    this.objects = this.isCuratedGroupsMode ? this.myCuratedGroups : this.$currentUser.myCohorts // eslint-disable-line vue/no-mutating-props
    this.type = this.isCuratedGroupsMode ? 'curated' : 'cohort'
  },
  methods: {
    addItem(object) {
      this.added.push(object)
      this.addObject(object)
      this.alertScreenReader(`${this.header} ${object.name} added to batch note`)
    },
    remove(object) {
      this.added = this.$_.filter(this.added, a => a.id !== object.id)
      this.removeObject(object)
      this.alertScreenReader(`${this.header} ${object.name} removed from batch note`)
    }
  }
}
</script>
