import {Plugin, icons} from 'ckeditor5'
import {createButton} from '@/plugins/ckeditor/utils'

export default class BoldCustom extends Plugin {
  static get pluginName() {
    return 'BoldCustom'
  }

  static get isOfficialPlugin() {
    return true
  }

  init(): void {
    const editor = this.editor
    const t = editor.locale.t
    const button = createButton({
      editor,
      commandName: 'bold',
      plugin: this,
      icon: icons.bold,
      label: t( 'Bold' ),
      keystroke: 'CTRL+B'
    })
    editor.ui.componentFactory.add('boldCustom', () => button)
  }
}
