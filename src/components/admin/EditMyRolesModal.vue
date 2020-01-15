<template>
  <b-modal
    id="edit-my-roles-modal"
    v-model="showEditRolesModal"
    :no-close-on-backdrop="true"
    body-class="pl-0 pr-0"
    hide-footer
    hide-header
    @cancel.prevent="cancel"
    @hide.prevent="cancel">
    <div>
      <div class="modal-header">
        <h2 id="edit-modal-header" class="student-section-header">{{ dept.name }}</h2>
      </div>
      <div class="modal-body m-0 p-0">
        <div class="ml-3 mr-2 p-2">
          <div class="pl-4">
            <div class="align-items-center d-flex">
              <div class="font-weight-500 pr-2 pt-1">
                <label :for="`select-department-${deptCode}-role`">Role:</label>
              </div>
              <b-form-select
                :id="`select-department-${deptCode}-role`"
                v-model="selectedRole"
                required
                :options="[
                  { text: 'Drop-In Advisor', value: 'dropInAdvisor' }
                ]"
                :aria-label="`Your role in ${dept.name}`"
                class="w-260px">
              </b-form-select>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <b-btn
            id="save-changes-to-user-profile"
            class="btn-primary-color-override"
            variant="primary"
            @click="save()">
            Save
          </b-btn>
          <b-btn
            id="delete-cancel"
            class="pl-2"
            variant="link"
            @click="cancel()"
            @keyup.enter="cancel()">
            Cancel
          </b-btn>
        </div>
      </div>
    </div>
  </b-modal>
</template>

<script>
import Berkeley from '@/mixins/Berkeley';
import Context from '@/mixins/Context';
import Util from '@/mixins/Util';
import { updateDropInRole } from '@/api/user';

export default {
  name: 'EditMyRolesModal',
  mixins: [Berkeley, Context, Util],
  props: {
    afterSave: {
      required: true,
      type: Function
    },
    cancel: {
      type: Function,
      required: false
    },
    deptCode: {
      type: String,
      required: true
    },
    showModal: {
      type: Boolean,
      required: true
    }
  },
  data: () => ({
    dept: undefined,
    selectedRole: undefined,
    showEditRolesModal: false
  }),
  created() {
    this.dept = this.find(this.$currentUser.departments, {'code': this.deptCode.toUpperCase()});
    this.showEditRolesModal = this.showModal;
    this.setRole();
  },
  methods: {
    save() {
      updateDropInRole(this.deptCode, this.selectedRole).then(() => {
        this.afterSave();
        this.selectedRole = undefined;
        this.closeModal();
      }).catch(error => {
        this.error = this.get(error, 'response.data.message') || error;
      });
    },
    setRole() {
      if (this.dept) {
        const dropInAdvisorDept = this.find(this.$currentUser.dropInAdvisorStatus, {'deptCode': this.deptCode.toUpperCase()});
        if (dropInAdvisorDept) {
          this.selectedRole = 'dropInAdvisor';
        }
      }
    }
  }
}
</script>