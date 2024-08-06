<template>
  <div>
    <div class="mt-3 w-75">
      <div v-if="showWarning" class="alert-box pa-3 mt-2 mb-3 w-100 warning">
        <span v-if="warning">{{ warning }}</span>
        <span v-if="!sids.length || sidsNotFound.length">
          <span v-if="sids.length"> {{ sidsNotFound.length === 1 ? 'Remove from list?' : 'Remove these from your list?' }}</span>
          <v-btn
            id="remove-invalid-sids-btn"
            class="font-weight-700 mb-1 pl-2"
            variant="link"
            @click="scrub"
          >
            {{ sids.length ? 'Yes' : 'Clear the textarea.' }}
          </v-btn>
        </span>
        <ul v-if="sids.length && sidsNotFound.length && (sidsNotFound.length <= magicNumber)" id="sids-not-found" class="mb-0 mt-1">
          <li v-for="sid in sidsNotFound" :key="sid">{{ sid }}</li>
        </ul>
      </div>
      <div>
        <v-textarea
          id="curated-group-bulk-add-sids"
          v-model="textarea"
          label="Enter SIDs here"
          variant="outlined"
          :disabled="isValidating || isSaving"
          clearable
        />
      </div>
      <div class="d-flex justify-content-end mt-3">
        <v-btn
          id="btn-curated-group-bulk-add-sids"
          class="px-3"
          :disabled="!_trim(textarea) || isValidating || isSaving"
          color="blue-darken-4"
          variant="flat"
          @click="submit"
        >
          <span v-if="isValidating || isSaving"><v-progress-circular size="small" /> <span class="pl-1">Adding</span></span>
          <span v-if="!isValidating && !isSaving">{{ curatedGroupId ? 'Add' : 'Next' }}</span>
        </v-btn>
        <v-btn
          v-if="curatedGroupId"
          id="btn-cancel-bulk-add-sids"
          variant="link"
          @click="cancel"
        >
          Cancel
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import {alertScreenReader} from '@/lib/utils'
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
    domain: {
      default: undefined,
      required: false,
      type: String
    },
    isSaving: {
      required: false,
      type: Boolean
    }
  },
  data: () => ({
    error: undefined,
    isValidating: false,
    magicNumber: 15,
    showWarning: false,
    sids: [],
    sidsNotFound: [],
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
        this.clearWarning()
        this.bulkAddSids(null)
      }
    },
    clearWarning() {
      this.showWarning = false
      this.warning = undefined
    },
    scrub() {
      this.sids = this._uniq(this.sids)
      this.textarea = this.sids.length ? this.sids.join(', ') : ''
      alertScreenReader(`${this.sidsNotFound.length} invalid SIDs removed from textarea.`)
      this.sidsNotFound = []
      this.clearWarning()
    },
    setWarning(message) {
      this.warning = message
      this.showWarning = true
      alertScreenReader(message)
    },
    submit() {
      this.sids = []
      this.sidsNotFound = []
      this.clearWarning()

      const trimmed = this._trim(this.textarea, ' ,\n\t')
      if (trimmed) {
        const split = this._split(trimmed, /[,\r\n\t ]+/)
        const notNumeric = this._partition(split, sid => /^\d+$/.test(this._trim(sid)))[1]
        if (notNumeric.length) {
          this.setWarning('SIDs must be numeric and separated by commas, line breaks, or tabs.')
          this.putFocusNextTick('curated-group-bulk-add-sids')
        } else {
          this.isValidating = true
          validateSids(this.domain, split).then(data => {
            this._each(data, entry => {
              switch(entry.status) {
              case 200:
              case 401:
                this.sids.push(entry.sid)
                break
              default:
                this.sidsNotFound.push(entry.sid)
              }
            })
            this.sidsNotFound = this._uniq(this.sidsNotFound)
            this.isValidating = false
            if (this.sidsNotFound.length) {
              const label = this.domain === 'admitted_students' ? 'admit' : 'student'
              if (this.sids.length) {
                this.setWarning(this.sidsNotFound.length === 1 ? `One ${label} not found.` : `${this.sidsNotFound.length} ${label}s not found.`)
              } else {
                this.setWarning(`No matching ${label}${this.sidsNotFound.length === 1 ? '' : 's'} found.`)
              }
            } else {
              this.bulkAddSids(this._uniq(this.sids))
              this.sids = []
            }
          })
        }
      } else {
        this.setWarning('Please provide one or more SIDs.')
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
.warning {
  background-color: #fbf7dc;
  color: #795f31;
  margin-bottom: 18px !important;
  padding: 10px 20px;
  border-radius: 4px;
}
</style>
