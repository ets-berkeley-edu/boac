<template>
  <v-tooltip
    :id="`${idPrefix}-author-details`"
    attach
    close-delay="500"
    content-class="bg-white elevation-2"
    eager
    interactive
    location="bottom end"
    scroll-strategy="reposition"
  >
    <template #activator="{ props: tooltipProps }">
      <div v-if="!name && !email" class="text-medium-emphasis" :class="activatorClass">
        Advisor profile not found
      </div>
      <router-link
        v-if="showPeerAdvisorLink"
        :id="`${idPrefix}-link-to-peer-advisor-home`"
        v-bind="tooltipProps"
        :aria-describedby="undefined"
        :aria-details="`${idPrefix}-author-details`"
        class="text-no-wrap text-primary pl-2"
        :class="activatorClass"
        :to="`/peer_advisor/${author.uid}/home`"
      >
        <span class="mr-1 text-wrap">{{ name }}</span><v-icon class="mb-1" :icon="mdiInformation" size="1rem" />
      </router-link>
      <div
        v-if="!showPeerAdvisorLink && (name || email)"
        :id="`${idPrefix}-author-name`"
        v-bind="tooltipProps"
        :aria-describedby="undefined"
        :aria-details="`${idPrefix}-author-details`"
        class="text-no-wrap text-primary pl-2"
        :class="activatorClass"
        role="button"
        tabindex="0"
      >
        <span class="mr-1 text-wrap">{{ name || email }}</span><v-icon class="mb-1" :icon="mdiInformation" size="1rem" />
      </div>
    </template>
    <div class="pa-2">
      <div :aria-hidden="true" class="font-weight-bold">{{ name }}</div>
      <span v-if="role">
        <span :id="`${idPrefix}-author-role`">{{ capitalizeAllWords(replace(role, '_', ' ')) }}</span>
      </span>
      <div v-if="peerAdvisingDepartment">
        <span :id="`${idPrefix}-peer-advising-department`">{{ peerAdvisingDepartment.name }}</span>
        <div
          v-if="peerAdvisingDepartment.deptName !== peerAdvisingDepartment.name"
          :id="`${idPrefix}-university-department-of-peer-advisor`"
          class="text-medium-emphasis"
        >
          {{ peerAdvisingDepartment.deptName }}
        </div>
      </div>
      <div v-if="!peerAdvisingDepartment" class="text-medium-emphasis">
        <div v-for="(deptName, index) in departments" :key="index">
          <span :id="`${idPrefix}-author-dept-${index}`">{{ deptName }}</span>
        </div>
      </div>
      <hr>
      <a
        :id="`${idPrefix}-author-directory-link`"
        :aria-label="`${name} UC Berkeley Directory page (opens in new tab)`"
        class="d-flex align-center"
        :href="`https://www.berkeley.edu/directory/results?search-term=${name}`"
        target="_blank"
      >
        View directory listing <v-icon class="ml-2" :icon="mdiOpenInNew" size="1rem" />
      </a>
    </div>
  </v-tooltip>
</template>

<script setup lang="ts">
import {computed, onMounted, ref} from 'vue'
import {map, orderBy, replace} from 'lodash'
import {mdiInformation, mdiOpenInNew} from '@mdi/js'
import {capitalizeAllWords, oxfordJoin} from '@/lib/utils'
import {findPeerAdvisingDepartment, getBoaUserRoles} from '@/lib/berkeley-department'
import {getCalnetProfileByCsid, getCalnetProfileByUid} from '@/api/user'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  activatorClass: {
    default: '',
    required: false,
    type: String
  },
  author: {
    required: true,
    type: Object
  },
  idPrefix: {
    default: 'note',
    required: false,
    type: String
  },
  peerAdvisingDepartmentId: {
    default: undefined,
    required: false,
    type: Number
  }
})

const departments = ref(orderBy(map(props.author.departments, 'deptName')))
const email = ref(props.author.email)
const name = ref(props.author.name)
const role = ref(props.author.role || props.author.title)
const contextStore = useContextStore()
const peerAdvisingDepartment = ref()
const showPeerAdvisorLink = computed(() => contextStore.currentUser.isAdmin && props.peerAdvisingDepartmentId && props.author.uid && name.value)

onMounted(() => {
  if (!name.value || !role.value) {
    loadAuthorDetails()
  }
  if (props.peerAdvisingDepartmentId) {
    peerAdvisingDepartment.value = findPeerAdvisingDepartment(props.peerAdvisingDepartmentId)
  }
})

const loadAuthorDetails = () => {
  const setAuthorDetails = author => {
    email.value = author.email
    name.value = author.name
    role.value = author.role || author.title
    departments.value = orderBy(map(author.departments, 'deptName'))
    if (!role.value && author.departments.length) {
      role.value = oxfordJoin(getBoaUserRoles(author.departments[0]))
    }
  }
  if (props.author.uid) {
    if (props.author.uid === contextStore.currentUser.uid) {
      setAuthorDetails(contextStore.currentUser)
    } else {
      getCalnetProfileByUid(props.author.uid).then(setAuthorDetails)
    }
  } else if (props.author.sid) {
    getCalnetProfileByCsid(props.author.sid).then(setAuthorDetails)
  }
}
</script>
