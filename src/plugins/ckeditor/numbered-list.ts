import {IconNumberedList, Plugin} from 'ckeditor5'
import {createButton} from '@/plugins/ckeditor/utils'

export default class ListNumberedCustom extends Plugin {
  static get pluginName() {
    return 'ListNumberedCustom'
  }

  static get isOfficialPlugin() {
    return true
  }

  init(): void {
    const editor = this.editor
    const t = editor.locale.t
    const button = createButton({
      editor,
      commandName: 'numberedList',
      plugin: this,
      icon: IconNumberedList,
      label: t('Numbered List')
    })
    editor.ui.componentFactory.add('listNumberedCustom', () => button)
  }
}
