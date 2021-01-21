<template>
  <div>
    <div class="mt-3 w-75">
      <div
        v-if="error || warning"
        :class="{'error': error, 'warning': warning}"
        class="alert-box p-3 mt-2 mb-3 w-100"
        v-html="error || warning"
      />
      <div>
        <b-form-textarea
          id="curated-group-bulk-add-sids"
          v-model="textarea"
          :disabled="isValidating || isSaving"
          aria-label="Type or paste student SID numbers here"
          rows="8"
          max-rows="30"
          @keydown.esc="cancel"
        ></b-form-textarea>
      </div>
      <div class="d-flex justify-content-end mt-3">
        <b-btn
          id="btn-curated-group-bulk-add-sids"
          class="pl-2"
          :disabled="!$_.trim(textarea) || isValidating || isSaving"
          variant="primary"
          @click="submitSids"
        >
          <span v-if="isValidating || isSaving"><font-awesome icon="spinner" spin /> <span class="pl-1">Adding</span></span>
          <span v-if="!isValidating && !isSaving">{{ curatedGroupId ? 'Add' : 'Next' }}</span>
        </b-btn>
        <b-btn
          v-if="curatedGroupId"
          id="btn-cancel-bulk-add-sids"
          variant="link"
          @click="cancel"
        >
          Cancel
        </b-btn>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import { validateSids } from '@/api/student'

export default {
  name: 'CuratedGroupBulkAdd',
  mixins: [Context, Util],
  props: {
    bulkAddSids: Function,
    curatedGroupId: Number,
    isSaving: {
      type: Boolean
    }
  },
  data: () => ({
    error: undefined,
    isValidating: false,
    sids: undefined,
    textarea: undefined,
    warning: undefined
  }),
  created() {
    this.putFocusNextTick('curated-group-bulk-add-sids')
  },
  methods: {
    cancel() {
      if (this.curatedGroupId) {
        // Cancel is only supported in the add-students-to-existing-group case.
        this.clearErrors()
        this.bulkAddSids(null)
      }
    },
    clearErrors() {
      this.error = null
      this.warning = null
    },
    submitSids() {
      this.sids = []
      this.clearErrors()
      const trimmed = this.$_.trim(this.textarea, ' ,\n\t')
      if (trimmed) {
        const split = this.$_.split(trimmed, /[,\r\n\t ]+/)
        const notNumeric = this.$_.partition(split, sid => /^\d+$/.test(this.$_.trim(sid)))[1]
        if (notNumeric.length) {
          this.error = 'SIDs must be separated by commas, line breaks, or tabs.'
          this.alertScreenReader(this.error)
          this.putFocusNextTick('curated-group-bulk-add-sids')
        } else {
          this.isValidating = true
          validateSids(split).then(data => {
            const notFound = []
            this.$_.each(data, entry => {
              switch(entry.status) {
              case 200:
              case 401:
                this.sids.push(entry.sid)
                break
              default:
                notFound.push(entry.sid)
              }
            })
            this.isValidating = false
            if (notFound.length === 1) {
              this.warning = `Student ${notFound[0]} not found.`
              this.alertScreenReader(this.warning)
            } else if (notFound.length > 1) {
              this.warning = `${notFound.length} students not found: <ul class="mt-1 mb-0"><li>${this.$_.join(notFound, '</li><li>')}</li></ul>`
              this.alertScreenReader(`Student IDs not found: ${this.oxfordJoin(notFound)}`)
            } else {
              this.clearErrors()
              this.bulkAddSids(this.sids)
            }
          })
        }
      } else {
        this.warning = 'Please provide one or more SIDs.'
        this.alertScreenReader(this.warning)
        this.putFocusNextTick('curated-group-bulk-add-sids')
      }
    }
  }
}
</script>

<style scoped>
.alert-box {
  border-radius: 5px;
  font-size: 18px;
  width: auto;
}
.error {
  background-color: #efd6d6;
  color: #9b393a;
}
.warning {
  background-color: #fbf7dc;
  color: #795f31;
}
</style>
