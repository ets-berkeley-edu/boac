<template>
  <div class="w-100">
    <div
      v-if="!isOpen"
      :id="`appointment-${appointment.id}-is-closed`"
      class="appointment-snippet-when-closed d-flex"
    >
      <div
        :id="`appointment-${appointment.id}-details-closed`"
        class="flex-grow-1 truncate-with-ellipsis"
        v-html="summarizeNoteForAcademicTimeline(appointment, !isOpen)"
      />
      <AppointmentCanceledIndicator
        v-if="!isOpen && ['Calendly', 'YCBM'].includes(appointment.createdBy) && (appointment.status === 'cancelled' || appointment.isRescheduled || appointment.isStudentNoShow)"
        :id="`collapsed-${appointment.type}-${appointment.id}-status-cancelled`"
        :appointment="appointment"
        class="collapsed-cancelled-icon"
      />
      <div v-if="size(appointment.attachments)" class="px-2">
        <v-icon :aria-hidden="true" color="info" :icon="mdiPaperclip" />
        <span class="sr-only">Has attachments</span>
      </div>
    </div>
    <div class="advising-appointment-outer">
      <div
        :id="`appointment-${appointment.id}-is-open`"
        class="pb-4"
        :class="{'sr-only': !isOpen}"
      >
        <h3 :id="`appointment-${appointment.id}-title`" class="font-size-18 pr-10">
          <span v-if="appointment.appointmentTitle" v-html="appointment.appointmentTitle" />
          <span v-if="!appointment.appointmentTitle">{{ summaryHeading }}</span>
        </h3>
        <div
          :id="`appointment-${appointment.id}-details`"
          class="py-3"
          v-html="appointment.details"
        />
        <div
          v-if="appointment.status === 'cancelled' || appointment.isRescheduled || appointment.isStudentNoShow"
          :id="`appointment-${appointment.id}-${appointment.status === 'cancelled' ? 'canceled' : (appointment.isStudentNoShow ? 'no-show' : 'rescheduled')}`"
          class="py-3"
        >
          <AppointmentCanceledIndicator
            :appointment="appointment"
            show-reason
          />
        </div>
        <div
          v-if="get(advisor, 'name') && (appointment.legacySource || ['Calendly', 'YCBM'].includes(appointment.createdBy))"
          class="pt-2"
        >
          <a
            v-if="advisor.uid"
            :id="`appointment-${appointment.id}-advisor-name`"
            :aria-label="`${advisor.name} UC Berkeley Directory page (opens in new tab)`"
            :href="`https://www.berkeley.edu/directory/results?search-term=${advisor.name}`"
            target="_blank"
          >
            {{ advisor.name }}
          </a>
          <span v-if="!advisor.uid" :id="`appointment-${appointment.id}-advisor-name`">
            {{ advisor.name }}
          </span>
          <span v-if="advisor.title" :id="`appointment-${appointment.id}-advisor-role`">
            - {{ advisor.title }}
          </span>
          <span v-if="appointment.legacySource" class="font-italic text-medium-emphasis">
            (appointment imported from {{ appointment.legacySource }})
          </span>
        </div>
        <div v-if="size(get(advisor, 'departments'))" class="text-medium-emphasis">
          <span v-for="(dept, index) in advisor.departments" :key="dept.deptCode">
            <span :id="`appointment-${appointment.id}-advisor-dept-${index}`">{{ dept.deptName }}</span>
          </span>
        </div>
        <div
          v-if="appointment.appointmentType"
          :id="`appointment-${appointment.id}-type`"
          class="pt-2"
          :class="{'text-medium-emphasis': ['Calendly', 'YCBM'].includes(appointment.appointmentType)}"
        >
          {{ appointment.appointmentType }}
        </div>
        <div v-if="appointment.topics && size(appointment.topics)" class="pt-3">
          <div :id="`appointment-${appointment.id}-topics-label`" class="font-size-16 font-weight-bold text-medium-emphasis pb-1">
            Topics
          </div>
          <ul :aria-labelledby="`appointment-${appointment.id}-topics-label`" class="list-no-bullets">
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
        <div v-if="appointment.attachments && size(appointment.attachments)" class="pt-3">
          <div :id="`appointment-${appointment.id}-attachments-label`" class="font-size-16 font-weight-bold text-medium-emphasis pb-1">
            Attachments
          </div>
          <ul :aria-labelledby="`appointment-${appointment.id}-attachments-label`" class="list-no-bullets">
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
import {computed, onMounted, ref, watch} from 'vue'
import {get, size} from 'lodash'
import {mdiPaperclip} from '@mdi/js'
import AppointmentCanceledIndicator from '@/components/appointment/AppointmentCanceledIndicator'
import {getCalnetProfileByCsid, getCalnetProfileByUid} from '@/api/user'
import PillItem from '@/components/util/PillItem'
import {useContextStore} from '@/stores/context'
import {summarizeNoteForAcademicTimeline} from '@/lib/note.js'

const props = defineProps({
  appointment: {
    required: true,
    type: Object
  },
  isOpen: {
    required: true,
    type: Boolean
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
  return get(props.appointment, 'advisor.name') ? `${heading}: ${props.appointment.advisor.name}` : heading
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
}
.collapsed-cancelled-icon {
  margin-top: -2px;
  padding: 0 10px;
}
:deep(.collapsed-cancelled-icon .v-alert__prepend) {
  margin-inline-end: 4px !important;
}
</style>
