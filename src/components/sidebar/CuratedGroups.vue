<template>
  <div>
    <div class="d-flex justify-content-between mb-1 sidebar-row-link">
      <div class="ml-2 sidebar-header">
        Curated Groups
      </div>
      <div class="ml-2 mr-2">
        <a
          id="create-curated-group-from-sidebar"
          class="sidebar-create-link"
          aria-label="Create a new curated group"
          href=""
          @click.prevent="updatePath('curate')"
        ><i class="fas fa-plus sidebar-header"></i>
        </a>
      </div>
    </div>
    <div
      v-for="(group, index) in myCuratedGroups"
      :key="group.id"
      class="d-flex justify-content-between sidebar-row-link">
      <div class="ml-2 truncate-with-ellipsis">
        <a
          :id="`sidebar-curated-group-${index}`"
          :aria-label="'Curated group ' + group.name + ' has ' + group.studentCount + ' students'"
          href=""
          @click.prevent="updatePath(`/curated/${group.id}`)">
          {{ group.name }}
        </a>
      </div>
      <div class="ml-2 mr-2">
        <span
          :id="`sidebar-curated-group-${index}-count`"
          class="sidebar-pill">{{ group.studentCount }}<span class="sr-only">{{ 'student' | pluralize(group.studentCount) }}</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import router from '@/router';

export default {
  name: 'CuratedGroups',
  mixins: [UserMetadata, Util],
  methods: {
    updatePath(path) {
      router.push(this.forceUniquePath(path));
    }
  }
};
</script>
