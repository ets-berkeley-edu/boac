<template>
  <div>
    <div class="text-grey-darken-2">Date Range</div>
    <b-form @submit="onSubmit">
      <b-form-group>
        <div class="align-items-end d-flex pt-2">
          <div>
            <label for="alerts-log-export-from-date">
              <span class="sr-only">Date</span>
              From
            </label>
            <v-date-picker
              v-model="fromDate"
              :max-date="toDate || maxDate"
              :min-date="minDate"
              popover-visibility="focus"
            >
              <template #default="{inputValue, inputEvents}">
                <input
                  id="alerts-log-export-from-date"
                  class="date-input form-control"
                  :disabled="isDownloading"
                  :placeholder="dateInputFormat"
                  :value="inputValue"
                  v-on="inputEvents"
                />
              </template>
            </v-date-picker>
          </div>
          <div class="pl-3">
            <label for="alerts-log-export-to-date">
              <span class="sr-only">Date</span>
              To
            </label>
            <v-date-picker
              v-model="toDate"
              :max-date="maxDate"
              :min-date="fromDate || minDate"
              popover-visibility="focus"
            >
              <template #default="{inputValue, inputEvents}">
                <input
                  id="alerts-log-export-to-date"
                  class="date-input form-control"
                  :disabled="isDownloading"
                  :placeholder="dateInputFormat"
                  :value="inputValue"
                  v-on="inputEvents"
                />
              </template>
            </v-date-picker>
          </div>
          <div class="pl-3">
            <b-button
              id="alerts-log-export-submit"
              class="btn-primary-color-override"
              :disabled="isDownloading || !fromDate || !toDate"
              variant="primary"
              @click="onSubmit"
            >
              <span v-if="isDownloading"><font-awesome icon="spinner" spin /> Fetching CSV</span>
              <span v-if="!isDownloading">Export</span>
            </b-button>
          </div>
        </div>
      </b-form-group>
    </b-form>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import {downloadAlertsCSV} from '@/api/reports'

export default {
  name: 'AlertsLogExport',
  mixins: [Context, Util],
  data: () => ({
    dateInputFormat: 'MM/DD/YYYY',
    fromDate: undefined,
    isDownloading: false,
    maxDate: new Date(),
    minDate: new Date('01/01/2014'),
    toDate: undefined
  }),
  methods: {
    onSubmit() {
      this.isDownloading = true
      downloadAlertsCSV(
        this.moment(this.fromDate).format(this.dateInputFormat),
        this.moment(this.toDate).format(this.dateInputFormat)
      ).then(() => {
        this.alertScreenReader('Alerts CSV file downloaded')
        this.isDownloading = false
      })
    }
  }
}
</script>

<style scoped>
.date-input {
  width: 130px;
}
</style>
