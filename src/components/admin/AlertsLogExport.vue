<template>
  <div>
    <div class="text-muted">Date Range</div>
    <b-form @submit="onSubmit">
      <b-form-group>
        <div class="align-items-end d-flex pt-2">
          <div>
            <label for="alerts-log-export-from-date">
              <span class="sr-only">Date</span>
              From
            </label>
            <v-date-picker v-model="fromDate" :max-date="toDate || maxDate" :min-date="minDate">
              <template v-slot="{inputValue, inputEvents}">
                <b-input-group>
                  <b-form-input
                    id="alerts-log-export-from-date"
                    class="date-input"
                    :disabled="isDownloading"
                    :formatter="dateFormat"
                    :placeholder="dateInputFormat"
                    :value="inputValue"
                    v-on="inputEvents"
                  />
                </b-input-group>
              </template>
            </v-date-picker>
          </div>
          <div class="pl-3">
            <label for="alerts-log-export-to-date">
              <span class="sr-only">Date</span>
              To
            </label>
            <v-date-picker v-model="toDate" :max-date="maxDate" :min-date="fromDate || minDate">
              <template v-slot="{inputValue, inputEvents}">
                <b-input-group>
                  <b-form-input
                    id="alerts-log-export-to-date"
                    class="date-input"
                    :disabled="isDownloading"
                    :formatter="dateFormat"
                    :placeholder="dateInputFormat"
                    :value="inputValue"
                    v-on="inputEvents"
                  />
                </b-input-group>
              </template>
            </v-date-picker>
          </div>
          <div class="pl-3">
            <b-button
              id="alerts-log-export-submit"
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
import {downloadAlertsCSV} from '@/api/reports'

export default {
  name: 'AlertsLogExport',
  mixins: [Context],
  data: () => ({
    dateInputFormat: 'MM/DD/YYYY',
    fromDate: undefined,
    isDownloading: false,
    maxDate: new Date(),
    minDate: new Date('01/01/2014'),
    toDate: undefined
  }),
  methods: {
    dateFormat(value) {
      const parsed = Date.parse(value)
      return isNaN(parsed) ? null : this.$options.filters.moment(parsed, this.dateInputFormat)
    },
    onSubmit() {
      this.isDownloading = true
      downloadAlertsCSV(
        this.$options.filters.moment(this.fromDate, this.dateInputFormat),
        this.$options.filters.moment(this.toDate, this.dateInputFormat)
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
