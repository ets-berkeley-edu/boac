<template>
  <div>
    <div>
      <label
        :id="`${ckElementId}-label`"
        :for="ckElementId"
        class="font-size-16 font-weight-bolder mt-3 mb-1"
      >
        {{ label }}
      </label>
    </div>
    <div
      :id="ckElementId"
      :aria-labelledby="`${ckElementId}-label`"
      role="textbox"
    >
      <ckeditor
        :value="initialValue"
        :disabled="disabled"
        :editor="editor"
        :config="editorConfig"
        @input="onUpdate"
      ></ckeditor>
    </div>
  </div>
</template>

<script>
import ClassicEditor from '@ckeditor/ckeditor5-build-classic'
import Util from '@/mixins/Util'

require('@/assets/styles/ckeditor-custom.css')

export default {
  name: 'RichTextEditor',
  mixins: [Util],
  props: {
    disabled: {
      required: false,
      type: Boolean
    },
    editorConfig: {
      required: false,
      default: () => ({
        toolbar: ['bold', 'italic', 'bulletedList', 'numberedList', 'link'],
        typing: {
          transformations: {
            remove: ['oneForth', 'oneHalf', 'oneThird', 'threeQuarters', 'twoThirds']
          }
        }
      }),
      type: Object
    },
    initialValue: {
      required: true,
      type: String
    },
    isInModal: {
      required: false,
      type: Boolean
    },
    label: {
      required: true,
      type: String
    },
    onValueUpdate: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    domFixAttemptCount: 0,
    domFixer: undefined,
    editor: ClassicEditor,
    ckElementId: undefined
  }),
  watch: {
    isInModal() {
      this.initDomFixer()
    }
  },
  mounted() {
    this.ckElementId = `rich-text-editor-${new Date().getTime()}`
    this.initDomFixer()
  },
  methods: {
    correctTheDOM() {
      if (this.domFixAttemptCount === 10) {
        // Abort after N tries.
        clearInterval(this.domFixer)
      } else if (this.isInModal) {
        // When embedded in a modal, the CKEditor toolbar elements are unreachable because they are attached to
        // the end of the DOM and outside the modal. We must move these "ck" elements. The user should not notice.
        const ckEditorTool = 'ck ck-reset_all ck-body ck-rounded-corners'
        const elements = document.getElementsByClassName(ckEditorTool)
        if (elements.length > 0) {
          this.$_.each(elements, element => {
            document.getElementById(this.ckElementId).appendChild(element)
          })
          clearInterval(this.domFixer)
        } else {
          this.domFixAttemptCount++
        }
      } else {
        // We're not in a modal.
        clearInterval(this.domFixer)
      }
    },
    initDomFixer() {
      this.domFixAttemptCount = 0
      this.domFixer = setInterval(this.correctTheDOM, 500)
    },
    onUpdate(event) {
      this.onValueUpdate(this.$_.isString(event) ? event : event.target.value)
    }
  }
}
</script>
