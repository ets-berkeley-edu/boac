<template>
  <div v-if="myCuratedGroups && myCuratedGroups.length">
    <div class="sidebar-row sidebar-section-header">
      <div class="sidebar-header sidebar-row-link-label">
        <span class="sidebar-row-link-label-text">Curated Groups</span>
      </div>
    </div>
    <div class="sidebar-row-link"
         v-for="(group, index) in myCuratedGroups"
         :key="group.id">
      <div class="sidebar-row-link-label">
        <router-link :id="'sidebar-curated-cohort-' + index"
                     :aria-label="'Curated group ' + group.name + ' has ' + group.studentCount + ' students'"
                     class="sidebar-row-link-label-text"
                     :to="forceUniquePath(`/curated_group/${group.id}`)">{{ group.name }}</router-link>
      </div>
      <div>
        <span :id="'sidebar-curated-cohort-' + index + '-count'"
              class="sidebar-pill">{{group.studentCount}}<span class="sr-only">{{ 'student' | pluralize(group.studentCount) }}</span>
        </span>
      </div>
    </div>
    <hr class="section-divider"/>
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
