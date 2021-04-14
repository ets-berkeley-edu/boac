<template>
  <div>
    <Spinner />
    <div v-if="!loading">
      <div class="border-bottom light-blue-background pb-2">
        <StudentProfileHeader :compact="true" :student="student" />
      </div>
      <div class="m-3 pt-2">
        <h2 class="page-section-header">Create {{ student.firstName }}'s Degree Check</h2>
        <div>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore
          magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco nisi aliquip ex ea commodo consequat.
        </div>
        <div class="mt-3">
          <h3 class="font-size-18 font-weight-bold">Add Degree Check</h3>
        </div>
        <div v-if="templates.length">
          <div class="my-2 w-50">
            <b-select
              id="degree-template-select"
              v-model="selected"
              :disabled="isSaving"
              size="md"
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
                class="b-dd-override"
                :disabled="!selected"
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
import Loading from '@/mixins/Loading'
import Spinner from '@/components/util/Spinner'
import StudentProfileHeader from '@/components/student/profile/StudentProfileHeader'
import Util from '@/mixins/Util'
import {getStudentByUid} from '@/api/student'
import {getDegreeTemplates} from '@/api/degree'

export default {
  name: 'StudentDegreeCreate',
  mixins: [Context, Loading, Util],
  components: {
    Spinner,
    StudentProfileHeader
  },
  data: () => ({
    isSaving: false,
    selected: null,
    student: undefined,
    templates: undefined
  }),
  created() {
    const uid = this.$_.get(this.$route, 'params.uid')
    getStudentByUid(uid).then(data => {
      this.student = data
      this.setPageTitle(this.$currentUser.inDemoMode ? 'Student' : this.student.name)
      getDegreeTemplates().then(data => {
        this.templates = data
        this.loaded(`Create ${this.student.name}'s Degree Check`)
      })
    })
  },
  methods: {
    cancel() {
      this.$announcer.polite('Canceled')
    },
    onClickSave() {
      this.isSaving = true
      this.$announcer.polite('Saving')
      console.log('TODO: save')
      this.isSaving = false
    }
  }
}
</script>
