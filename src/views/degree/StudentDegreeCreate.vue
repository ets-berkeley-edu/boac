<template>
  <div>
    <Spinner />
    <div v-if="!loading">
      <div class="border-bottom light-blue-background pb-2">
        <StudentProfileHeader :compact="true" :link-to-student-profile="true" :student="student" />
      </div>
      <div class="m-3 pt-2">
        <h2 class="page-section-header">Create <span :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ student.firstName }}</span>'s Degree Check</h2>
        <div>
          Choose a new degree check for <span :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ student.name }}</span> from the list of options in the menu below.
        </div>
        <div class="mt-3">
          <h3 class="font-size-18 font-weight-bold">Add Degree Check</h3>
        </div>
        <div v-if="templates.length">
          <div class="my-2 w-30">
            <b-select
              id="degree-template-select"
              v-model="selectedOption"
              aria-label="Select a degree template"
              :disabled="isSaving"
              size="md"
              @change="onChangeSelect"
            >
              <b-select-option id="degree-check-select-option-null" :value="null">Choose...</b-select-option>
              <b-select-option
                v-for="option in templates"
                :id="`degree-check-select-option-${option.id}`"
                :key="option.id"
                required
                :value="option"
              >
                {{ option.name }}
              </b-select-option>
            </b-select>
          </div>
          <div class="d-flex mt-3">
            <div>
              <b-btn
                id="save-degree-check-btn"
                class="btn-primary-color-override"
                :disabled="!selectedOption"
                variant="primary"
                @click="onClickSave"
              >
                <span v-if="isSaving">
                  <font-awesome class="mr-1" icon="spinner" spin /> Saving
                </span>
                <span v-if="!isSaving">Save Degree Check</span>
              </b-btn>
            </div>
            <div>
              <b-btn
                id="cancel-create-degree-check-btn"
                :disabled="isSaving"
                variant="link"
                @click="cancel"
              >
                Cancel
              </b-btn>
            </div>
          </div>
        </div>
        <div v-if="!templates.length">
          No templates available.
          You can <router-link id="create-filtered-cohort" to="/degrees">create a Degree Check</router-link> and then
          return to this page to proceed.
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Spinner from '@/components/util/Spinner'
import store from '@/store'
import StudentProfileHeader from '@/components/student/profile/StudentProfileHeader'
import Util from '@/mixins/Util'
import {getStudentByUid} from '@/api/student'
import {createDegreeCheck, getDegreeTemplates} from '@/api/degree'

export default {
  name: 'StudentDegreeCreate',
  components: {Spinner, StudentProfileHeader},
  mixins: [Context, Util],
  data: () => ({
    isSaving: false,
    selectedOption: null,
    student: undefined,
    templates: undefined
  }),
  created() {
    let uid = this._get(this.$route, 'params.uid')
    if (this.currentUser.inDemoMode) {
      // In demo-mode we do not want to expose UID in browser location bar.
      uid = window.atob(uid)
    }
    getStudentByUid(uid, true).then(data => {
      this.student = data
      this.setPageTitle(this.currentUser.inDemoMode ? 'Student' : this.student.name)
      getDegreeTemplates().then(data => {
        this.templates = data
        store.dispatch('context/loadingComplete')
        this.$announcer.polite(`Add Degree Check for ${this.student.name}`)
      })
    })
  },
  methods: {
    cancel() {
      this.$announcer.polite('Canceled')
      this.$router.push(`${this.studentRoutePath(this.student.uid, this.currentUser.inDemoMode)}`)
    },
    onChangeSelect(option) {
      if (option) {
        this.$announcer.polite(`${this.selectedOption.name} selected`)
        this.putFocusNextTick('save-degree-check-btn')
      }
    },
    onClickSave() {
      this.isSaving = true
      this.$announcer.polite('Saving')
      createDegreeCheck(this.student.sid, this.selectedOption.id).then(data => {
        this.isSaving = false
        this.$router.push(`/student/degree/${data.id}`)
      })
    }
  }
}
</script>
