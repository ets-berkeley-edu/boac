import {Plugin, icons} from 'ckeditor5'
import {createButton} from '@/plugins/ckeditor/utils'

export default class ListBulletedCustom extends Plugin {
  static get pluginName() {
    return 'ListBulletedCustom'
  }

  static get isOfficialPlugin() {
    return true
  }

  init(): void {
    const editor = this.editor
    const t = editor.locale.t
    const button = createButton({
      editor,
      commandName: 'bulletedList',
      plugin: this,
      icon: icons.bulletedList,
      label: t('Bulleted List')
    })
    editor.ui.componentFactory.add('listBulletedCustom', () => button)
  }
}
