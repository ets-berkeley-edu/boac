<template>
  <div
    v-if="!isOpen"
    :id="`appointment-${appointment.id}-is-closed`"
    class="appointment-snippet-when-closed"
  >
    <span
      :id="`appointment-${appointment.id}-details-closed`"
      v-html="messageSummary"
    />
  </div>
  <div>
    <div class="advising-appointment-outer pb-3">
      <div v-if="isOpen" :id="`appointment-${appointment.id}-is-open`">
        <div v-if="appointment.appointmentTitle">
          <span :id="`appointment-${appointment.id}-title`" v-html="appointment.appointmentTitle" />
        </div>
        <div v-if="!appointment.appointmentTitle">
          <span :id="`appointment-${appointment.id}-title`">
            {{ summaryHeading }}
          </span>
        </div>
        <div class="mt-2">
          <span :id="`appointment-${appointment.id}-details`" v-html="appointment.details"></span>
        </div>
        <div
          v-if="appointment.status === 'cancelled'"
          class="mt-2"
          :class="{'border-sm pa-2': appointment.cancelReason}"
        >
          <div class="font-size-14 text-error text-uppercase">
            <v-icon class="mr-1" :icon="mdiCalendarMinus" />
            Canceled
          </div>
          <div v-if="appointment.cancelReason" class="mt-1 pl-7">
            <span :id="`appointment-${appointment.id}-cancel-reason`">{{ appointment.cancelReason }}</span>
          </div>
        </div>
        <div v-if="advisor.name && (appointment.legacySource || appointment.createdBy === 'YCBM')" class="mt-2">
          <a
            v-if="advisor.uid"
            :id="`appointment-${appointment.id}-advisor-name`"
            :aria-label="`Open UC Berkeley Directory page of ${advisor.name} in a new window`"
            :href="`https://www.berkeley.edu/directory/results?search-term=${advisor.name}`"
            target="_blank"
          >
            {{ advisor.name }}
          </a>
          <span v-if="!advisor.uid" :id="`appointment-${appointment.id}-advisor-name`">
            {{ advisor.name }}
          </span>
          <span v-if="advisor.title" :id="`appointment-${appointment.id}-advisor-role`" class="text-dark">
            - {{ advisor.title }}
          </span>
          <span v-if="appointment.legacySource" class="font-italic text-medium-emphasis">
            (appointment imported from {{ appointment.legacySource }})
          </span>
        </div>
        <div v-if="size(advisor.departments)" class="mt-2 text-medium-emphasis">
          <span v-for="(dept, index) in advisor.departments" :key="dept.code">
            <span :id="`appointment-${appointment.id}-advisor-dept-${index}`">{{ dept.name }}</span>
          </span>
        </div>
        <div v-if="appointment.appointmentType" :id="`appointment-${appointment.id}-type`" class="mt-2">
          {{ appointment.appointmentType }}
        </div>
        <div v-if="appointment.topics && size(appointment.topics)" class="mt-2">
          <div class="font-size-16 font-weight-bold">Topics</div>
          <ul class="list-no-bullets advising-note-pill-list">
            <li
              v-for="(topic, index) in appointment.topics"
              :key="topic"
            >
              <PillItem
                :id="`appointment-${appointment.id}-topic-${index}`"
                clazz="text-uppercase w-100"
                :label="topic"
                name="topic"
              >
                <span class="truncate-with-ellipses pr-1">
                  {{ topic }}
                </span>
              </PillItem>
            </li>
          </ul>
        </div>
        <div v-if="appointment.attachments && size(appointment.attachments)" class="mt-2">
          <div class="font-size-16 font-weight-bold">Attachments</div>
          <ul class="list-no-bullets advising-note-pill-list">
            <li
              v-for="(attachment, index) in appointment.attachments"
              :key="attachment.name"
            >
              <PillItem
                :id="`appointment-${appointment.id}-attachment-${index}`"
                :aria-label="`Download attachment ${attachment.displayName}`"
                :href="downloadUrl(attachment)"
                :icon="mdiPaperclip"
              >
                <span class="text-anchor truncate-with-ellipses pr-1">
                  {{ attachment.displayName }}
                </span>
              </PillItem>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import PillItem from '@/components/util/PillItem'
import {computed, onMounted, ref, watch} from 'vue'
import {get, size} from 'lodash'
import {getCalnetProfileByCsid, getCalnetProfileByUid} from '@/api/user'
import {mdiCalendarMinus, mdiPaperclip} from '@mdi/js'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  appointment: {
    required: true,
    type: Object
  },
  isOpen: {
    required: true,
    type: Boolean
  },
  messageSummary: {
    required: true,
    type: String
  },
  student: {
    required: true,
    type: Object
  }
})

const contextStore = useContextStore()
const advisor = ref(undefined)
const currentUser = contextStore.currentUser

watch(() => props.isOpen, () => {
  setAdvisor()
})

onMounted(() => {
  setAdvisor()
})

const downloadUrl = attachment => `${contextStore.config.apiBaseUrl}/api/appointments/attachment/${attachment.id}`

const summaryHeading = computed(() => {
  const heading = props.appointment.legacySource === 'SIS' ? 'Imported SIS Appt' : 'Advising Appt'
  if (get(props.appointment, 'advisor.name')) {
    return `${heading}: ${props.appointment.advisor.name}`
  } else {
    return heading
  }
})

const setAdvisor = () => {
  advisor.value = get(props.appointment, 'advisor')
  const requiresLazyLoad = props.isOpen && (!get(advisor.value, 'name') || !get(advisor.value, 'title'))
  if (requiresLazyLoad) {
    if (get(advisor.value, 'uid')) {
      if (advisor.value.uid === currentUser.uid) {
        advisor.value = currentUser
      } else {
        getCalnetProfileByUid(advisor.value.uid).then(data => {
          advisor.value = data
        })
      }
    } else if (get(advisor.value, 'sid')) {
      getCalnetProfileByCsid(advisor.value.sid).then(data => {
        advisor.value = data
      })
    } else {
      advisor.value = get(props.appointment, 'advisor')
    }
  }
}
</script>

<style scoped>
.advising-appointment-outer {
  flex-basis: 100%;
}
.appointment-snippet-when-closed {
  height: 24px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
