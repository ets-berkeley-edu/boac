<template>
  <div v-if="myCuratedGroups">
    <div class="sidebar-row-link sidebar-section-header">
      <div class="sidebar-header sidebar-row-link-label">
        <span class="sidebar-row-link-label-text">Curated Groups</span>
      </div>
      <div>
        <span class="sidebar-header sidebar-row-link-label">
          <router-link
            id="create-curated-group"
            class="sidebar-create-link pr-1"
            aria-label="Create a new curated group"
            :to="forceUniquePath('/curate/new/bulk_add')"><i class="fas fa-plus"></i></router-link>
        </span>
      </div>
    </div>
    <div
      v-for="(group, index) in myCuratedGroups"
      :key="group.id"
      class="sidebar-row-link">
      <div class="sidebar-row-link-label">
        <router-link
          :id="`sidebar-curated-group-${index}`"
          :aria-label="'Curated group ' + group.name + ' has ' + group.studentCount + ' students'"
          class="sidebar-row-link-label-text"
          :to="forceUniquePath(`/curate/${group.id}`)">
          {{ group.name }}
        </router-link>
      </div>
      <div>
        <span
          :id="`sidebar-curated-group-${index}-count`"
          class="sidebar-pill">{{ group.studentCount }}<span class="sr-only">{{ 'student' | pluralize(group.studentCount) }}</span>
        </span>
      </div>
    </div>
    <hr class="section-divider" />
  </div>
</template>

<script>
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'CuratedGroups',
  mixins: [UserMetadata, Util]
};
</script>

<style scoped>
.sidebar-row {
  line-height: 1.4em;
  padding: 1px 1px 1px 6px;
}
</style>
