<template>
  <div class="pt-5">
    <div class="align-items-center d-flex">
      <div class="pb-1 pl-2">
        <b-button
          class="m-0 p-0"
          :class="{'collapsed': showDebug}"
          aria-controls="collapse-degree-edit-debug"
          variant="link"
          @click="showDebug = !showDebug"
        >
          <div class="pb-1">
            <font-awesome :icon="showDebug ? 'caret-down' : 'caret-right'" :class="showDebug ? 'mr-1' : 'ml-1 mr-1'" />
            {{ showDebug ? 'Hide' : 'Show' }} degree-edit debug
          </div>
        </b-button>
      </div>
    </div>
    <b-collapse id="collapse-degree-edit-debug" v-model="showDebug">
      <div class="align-items-center d-flex py-2">
        <div class="font-weight-500 pb-1 pr-2">Degree_Edit_Session</div>
        <div v-if="disableButtons">
          <b-btn
            class="mb-1 px-0"
            variant="link"
            @click="setDisableButtons(false)"
          >
            Force enable buttons
          </b-btn>
        </div>
      </div>
      <div>
        <pre>{{ degreeEditSessionToString }}</pre>
      </div>
    </b-collapse>
  </div>
</template>

<script>
import DegreeEditSession from '@/mixins/DegreeEditSession'

export default {
  name: 'DebugDegreeTemplate',
  mixins: [DegreeEditSession],
  data: () => ({
    showDebug: false
  })
}
</script>
