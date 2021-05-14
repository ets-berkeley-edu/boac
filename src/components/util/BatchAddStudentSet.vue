<template>
  <div>
    <div>
      <label
        :for="`batch-${target}-${objectType}`"
        class="font-size-14 font-weight-bolder input-label text mt-2"
      ><span class="sr-only">Select a </span>{{ header }}</label>
    </div>
    <b-dropdown
      :id="`batch-${target}-${objectType}`"
      class="mb-2 ml-0 transparent"
      block
      :disabled="disabled"
      :lazy="true"
      menu-class="w-100"
      toggle-class="d-flex justify-content-between align-items-center"
      :text="isCuratedGroupsMode ? 'Add Group' : 'Add Cohort'"
      :aria-label="`${target} will be created for all students in selected ${objectType}${objects.length === 1 ? '' : 's'}`"
      variant="outline-dark"
    >
      <b-dropdown-item
        v-for="object in objects"
        :id="`batch-${target}-${objectType}-option-${object.id}`"
        :key="object.id"
        class="truncate-with-ellipsis"
        :aria-label="`Add ${objectType} ${object.name}`"
        :disabled="$_.includes(addedIds, object.id)"
        @click="add(object)"
      >
        {{ object.name }}
      </b-dropdown-item>
    </b-dropdown>
    <div>
      <div v-for="(addedObject, index) in added" :key="addedObject.id" class="mb-1">
        <span class="font-weight-bolder pill pill-attachment text-uppercase text-nowrap">
          <span :id="`batch-${target}-${objectType}-${index}`">{{ $_.truncate(addedObject.name) }}</span>
          <b-btn
            :id="`remove-${objectType}-from-batch-${index}`"
            variant="link"
            class="p-0"
            :disabled="disabled"
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
import CurrentUserExtras from '@/mixins/CurrentUserExtras'
import Util from '@/mixins/Util'

export default {
  name: 'BatchAddStudentSet',
  mixins: [Context, CurrentUserExtras, Util],
  props: {
    addObject: {
      required: true,
      type: Function
    },
    disabled: {
      required: false,
      type: Boolean
    },
    isCuratedGroupsMode: {
      required: true,
      type: Boolean
    },
    removeObject: {
      required: true,
      type: Function
    },
    target: {
      required: true,
      type: String
    }
  },
  data: () => ({
    added: [],
    header: undefined,
    objects: [],
    objectType: undefined
  }),
  computed: {
    addedIds() {
      return this.$_.map(this.added, 'id')
    }
  },
  created() {
    this.header = this.isCuratedGroupsMode ? 'Curated Group' : 'Cohort'
    this.objects = this.isCuratedGroupsMode ? this.myCuratedGroups : this.myCohorts
    this.objectType = this.isCuratedGroupsMode ? 'curated' : 'cohort'
  },
  methods: {
    add(object) {
      this.added.push(object)
      this.addObject(object)
      this.alertScreenReader(`${this.header} '${object.name}' added to batch ${this.target}`)
    },
    remove(object) {
      this.added = this.$_.filter(this.added, a => a.id !== object.id)
      this.removeObject(object)
      this.alertScreenReader(`${this.header} '${object.name}' removed`)
    }
  }
}
</script>
