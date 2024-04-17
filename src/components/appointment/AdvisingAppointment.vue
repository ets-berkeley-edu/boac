<template>
  <div :id="`appointment-${appointment.id}-outer`" class="advising-appointment-outer">
    <div
      v-if="!isOpen"
      :id="`appointment-${appointment.id}-is-closed`"
      :class="{'truncate-with-ellipsis': !isOpen}"
    >
      <span
        :id="`appointment-${appointment.id}-details-closed`"
        v-html="fallbackHeading(appointment)"
      />
    </div>
    <div v-if="isOpen" :id="`appointment-${appointment.id}-is-open`">
      <div v-if="appointment.appointmentTitle">
        <span :id="`appointment-${appointment.id}-title`" v-html="appointment.appointmentTitle" />
      </div>
      <div v-if="!appointment.appointmentTitle">
        <span :id="`appointment-${appointment.id}-title`">
          {{ summaryHeading(appointment) }}
        </span>
      </div>
      <div class="mt-2">
        <span :id="`appointment-${appointment.id}-details`" v-html="appointment.details"></span>
      </div>

      <div class="d-flex align-center mt-1 mb-3">
        <div v-if="appointment.status === 'cancelled'">
          <div class="font-size-14 my-3 text-red-lighten-2 text-uppercase">
            <v-icon :icon="mdiCalendarMinus" />
            Canceled
          </div>
          <div v-if="appointment.cancelReason" class="mt-1">
            <span :id="`appointment-${appointment.id}-cancel-reason`">{{ appointment.cancelReason }}</span>
          </div>
        </div>
      </div>
      <div v-if="advisor.name && (appointment.legacySource || appointment.createdBy === 'YCBM')" class="mt-2">
        <a
          v-if="advisor.uid"
          :id="`appointment-${appointment.id}-advisor-name`"
          :aria-label="`Open UC Berkeley Directory page of ${advisor.name} in a new window`"
          :href="`https://www.berkeley.edu/directory/results?search-term=${advisor.name}`"
          target="_blank"
        >{{ advisor.name }}</a>
        <span v-if="!appointment.advisor.uid" :id="`appointment-${appointment.id}-advisor-name`">
          {{ advisor.name }}
        </span>
        <span v-if="advisor.title" :id="`appointment-${appointment.id}-advisor-role`" class="text-dark">
          - {{ advisor.title }}
        </span>
        <span v-if="appointment.legacySource" class="font-italic text-black-50">
          (appointment imported from {{ appointment.legacySource }})
        </span>
      </div>
      <div v-if="_size(advisor.departments)" class="text-medium-emphasis">
        <span v-for="(dept, index) in advisor.departments" :key="dept.code">
          <span :id="`appointment-${appointment.id}-advisor-dept-${index}`">{{ dept.name }}</span>
        </span>
      </div>
      <div v-if="appointment.appointmentType" :id="`appointment-${appointment.id}-type`" class="mt-3">
        {{ appointment.appointmentType }}
      </div>
      <div v-if="appointment.topics && _size(appointment.topics)">
        <div class="pill-list-header mt-3 mb-1">{{ _size(appointment.topics) === 1 ? 'Topic' : 'Topics' }}</div>
        <ul class="pill-list pl-0">
          <li
            v-for="(topic, index) in appointment.topics"
            :id="`appointment-${appointment.id}-topic-${index}`"
            :key="topic"
            class="mt-2"
          >
            <span class="pill pill-attachment text-uppercase text-no-wrap">{{ topic }}</span>
          </li>
        </ul>
      </div>
      <div>
        <ul class="pill-list pl-0 mt-3">
          <li
            v-for="(attachment, index) in appointment.attachments"
            :id="`appointment-${appointment.id}-attachment-${index}`"
            :key="attachment.name"
            class="mt-2"
          >
            <span class="pill pill-attachment text-no-wrap">
              <a
                :id="`appointment-${appointment.id}-attachment-${index}`"
                :href="downloadUrl(attachment)"
              >
                <v-icon :icon="mdiPaperclip" />
                {{ attachment.displayName }}
              </a>
            </span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import {mdiCalendarMinus} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import {getCalnetProfileByCsid, getCalnetProfileByUid} from '@/api/user'
import {DateTime} from 'luxon'

export default {
  name: 'AdvisingAppointment',
  mixins: [Context, Util],
  props: {
    isOpen: {
      required: true,
      type: Boolean
    },
    appointment: {
      required: true,
      type: Object
    },
    student: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    advisor: undefined
  }),
  watch: {
    isOpen() {
      this.setAdvisor()
    }
  },
  created() {
    this.setAdvisor()
  },
  methods: {
    datePerTimezone(date) {
      return DateTime.fromJSDate(date).setZone(this.config.timezone)
    },
    downloadUrl(attachment) {
      return `${this.config.apiBaseUrl}/api/appointments/attachment/${attachment.id}`
    },
    fallbackHeading(appointment) {
      if (appointment.appointmentTitle && appointment.appointmentTitle.trim().length) {
        return appointment.appointmentTitle
      } else if (appointment.details && appointment.details.trim().length) {
        return appointment.details
      } else {
        return this.summaryHeading(appointment)
      }
    },
    setAdvisor() {
      this.advisor = this._get(this.appointment, 'advisor')
      const requiresLazyLoad = this.isOpen && (!this._get(this.advisor, 'name') || !this._get(this.advisor, 'title'))
      if (requiresLazyLoad) {
        if (this._get(this.advisor, 'uid')) {
          if (this.advisor.uid === this.currentUser.uid) {
            this.advisor = this.currentUser
          } else {
            getCalnetProfileByUid(this.advisor.uid).then(data => {
              this.advisor = data
            })
          }
        } else if (this._get(this.advisor, 'sid')) {
          getCalnetProfileByCsid(this.advisor.sid).then(data => {
            this.advisor = data
          })
        } else {
          this.advisor = this._get(this.appointment, 'advisor')
        }
      }
    },
    summaryHeading(appointment) {
      const heading = appointment.legacySource === 'SIS' ? 'Imported SIS Appt' : 'Advising Appt'
      if (appointment.advisor.name) {
        return `${heading}: ${appointment.advisor.name}`
      } else {
        return heading
      }
    }
  }
}
</script>

<style scoped>
.advising-appointment-outer {
  flex-basis: 100%;
}
</style>
