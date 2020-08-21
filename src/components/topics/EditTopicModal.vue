<template>
  <b-modal
    id="are-you-sure-modal"
    :no-close-on-backdrop="true"
    body-class="pl-0 pr-0"
    hide-footer
    hide-header
    @cancel.prevent="cancel"
    @hide.prevent="cancel"
    @shown="putFocusNextTick('are-you-sure-confirm')">
    <div>
      <div class="modal-header">
        <h3 id="are-you-sure-header">{{ topic.id ? 'Edit' : 'Create' }} Topic</h3>
      </div>
      <div class="modal-body">
        {{ topic }}
      </div>
      <div class="modal-footer">
        <form @submit.prevent="save">
          <b-btn
            id="are-you-sure-confirm"
            class="btn-primary-color-override"
            variant="primary"
            @click.prevent="save">
            Save
          </b-btn>
          <b-btn
            id="are-you-sure-cancel"
            class="pl-2"
            variant="link"
            @click.stop="cancel">
            Cancel
          </b-btn>
        </form>
      </div>
    </div>
  </b-modal>
</template>

<script>
import Context from '@/mixins/Context';

export default {
  name: 'EditTopicModal',
  mixins: [Context],
  props: {
    topic: {
      default: () => ({
        topic: '',
        availableInAppointments: false,
        availableInNotes: false
      }),
      required: false,
      type: Object
    }
  },
  methods: {
    cancel() {

    },
    save() {

    }
  }
}
</script>
