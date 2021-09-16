<template>
  <div>
    <div class="mt-3 w-75">
      <b-collapse v-model="showWarning" class="alert-box p-3 mt-2 mb-3 w-100 warning">
        <span v-if="warning">{{ warning }}</span>
        <span v-if="sidsNotFound.length">
          <span v-if="sids.length"> {{ sidsNotFound.length === 1 ? 'Remove from list?' : 'Remove these from your list?' }}</span>
          <b-btn
            id="remove-invalid-sids-btn"
            class="font-weight-bolder mb-1 pl-2"
            variant="link"
            @click="scrub"
          >
            {{ sids.length ? 'Yes' : 'Clear the textarea.' }}
          </b-btn>
        </span>
      </b-collapse>
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
          class="px-3"
          :disabled="!$_.trim(textarea) || isValidating || isSaving"
          variant="primary"
          @click="submit"
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
import {validateSids} from '@/api/student'

export default {
  name: 'CuratedGroupBulkAdd',
  mixins: [Context, Util],
  props: {
    bulkAddSids: {
      required: true,
      type: Function
    },
    curatedGroupId: {
      default: undefined,
      required: false,
      type: Number
    },
    isSaving: {
      required: false,
      type: Boolean
    }
  },
  data: () => ({
    error: undefined,
    isValidating: false,
    showWarning: false,
    sids: [],
    sidsNotFound: [],
    textarea: undefined,
    warning: undefined
  }),
  created() {
    this.$putFocusNextTick('curated-group-bulk-add-sids')
  },
  methods: {
    cancel() {
      if (this.curatedGroupId) {
        // Cancel is only supported in the add-students-to-existing-group case.
        this.clearWarning()
        this.bulkAddSids(null)
      }
    },
    clearWarning() {
      this.showWarning = false
      this.warning = undefined
    },
    scrub() {
      this.sids = this.$_.uniq(this.sids)
      this.textarea = this.sids.length ? this.sids.join(', ') : ''
      this.$announcer.polite(`${this.sidsNotFound.length} invalid SIDs removed from textarea.`)
      this.sidsNotFound = []
      this.clearWarning()
    },
    setWarning(message) {
      this.warning = message
      this.showWarning = true
      this.$announcer.polite(message)
    },
    submit() {
      this.sids = []
      this.sidsNotFound = []
      this.clearWarning()

      const trimmed = this.$_.trim(this.textarea, ' ,\n\t')
      if (trimmed) {
        const split = this.$_.split(trimmed, /[,\r\n\t ]+/)
        const notNumeric = this.$_.partition(split, sid => /^\d+$/.test(this.$_.trim(sid)))[1]
        if (notNumeric.length) {
          this.setWarning('SIDs must be numeric and separated by commas, line breaks, or tabs.')
          this.$putFocusNextTick('curated-group-bulk-add-sids')
        } else {
          this.isValidating = true
          validateSids(split).then(data => {
            this.$_.each(data, entry => {
              switch(entry.status) {
              case 200:
              case 401:
                this.sids.push(entry.sid)
                break
              default:
                this.sidsNotFound.push(entry.sid)
              }
            })
            this.sidsNotFound = this.$_.uniq(this.sidsNotFound)
            this.isValidating = false
            if (this.sidsNotFound.length) {
              if (this.sids.length) {
                this.setWarning(this.sidsNotFound.length === 1 ? 'One student not found.' : `${this.sidsNotFound.length} students not found.`)
              } else {
                this.setWarning(`No matching student${this.sidsNotFound.length === 1 ? '' : 's'} found.`)
              }
            } else {
              this.bulkAddSids(this.$_.uniq(this.sids))
              this.sids = []
            }
          })
        }
      } else {
        this.setWarning('Please provide one or more SIDs.')
        this.$putFocusNextTick('curated-group-bulk-add-sids')
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
.warning {
  background-color: #fbf7dc;
  color: #795f31;
}
</style>
