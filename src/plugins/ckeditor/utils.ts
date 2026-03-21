import {type AttributeCommand, ButtonView, type Editor, type Plugin} from 'ckeditor5'

/*
* Custom toolbar buttons behave the same as their CKEditor-provided counterparts,
* except they don't move focus to the textbox when you click them.
* Instead, the RichTextEditor component handles focus management.
*/
export function createButton(
  {
    editor, commandName, plugin, icon, label, keystroke
  }: {
    editor: Editor;
    commandName: string;
    icon: string;
    label: string;
    plugin: Plugin;
    keystroke?: string;
}
): ButtonView {
    const command = editor.commands.get(commandName) as AttributeCommand
    const button = new ButtonView(editor.locale)
    button.set({
      label,
      icon,
      keystroke,
      isToggleable: true,
      tooltip: true
    })
    button.bind('isEnabled').to(command, 'isEnabled')
    button.bind('isOn').to(command, 'value')

    plugin.listenTo(button, 'execute', () => {
      editor.execute(commandName)
    })
    return button
}
