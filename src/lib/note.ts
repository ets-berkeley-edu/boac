import {each, filter, get, isEmpty, size, trim} from 'lodash'
import {BoaConfig, useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

export function addFileDropEventListeners(): void {
  const preventFileDropOutsideFormControl = e => {
    const classList = get(e.target, 'classList', '')
    if (!classList.contains('choose-attachment-file-wrapper')) {
      e.preventDefault()
      e.dataTransfer.effectAllowed = 'none'
      e.dataTransfer.dropEffect = 'none'
    }
  }
  window.addEventListener('dragenter', preventFileDropOutsideFormControl, false)
  window.addEventListener('dragover', preventFileDropOutsideFormControl)
  window.addEventListener('drop', preventFileDropOutsideFormControl)
}

export function validateAttachment(attachments: any[], existingAttachments: any[]): string | null {
  const maxAttachmentMegabytes: number = 20
  const maxAttachmentBytes: number = maxAttachmentMegabytes * 1024 * 1024
  if (!(attachments && attachments.length)) {
    return 'No attachment provided.'
  }
  const config: BoaConfig = useContextStore().config
  if (size(attachments) + size(existingAttachments) > parseInt(config.maxAttachmentsPerNote)) {
    return `A note can have no more than ${config.maxAttachmentsPerNote} attachments.`
  }
  let error: string | null = null
  for (const attachment of attachments) {
    if (attachment.size > maxAttachmentBytes) {
      error = `The file '${attachment.name}' is too large. Attachments are limited to ${maxAttachmentMegabytes} MB in size.`
      break
    }
    const matching = filter(existingAttachments, a => attachment.name === a.displayName)
    if (matching.length) {
      error = `Another attachment has the name '${attachment.name}'. Please rename your file.`
      break
    }
  }
  return error
}

export function validateTemplateTitle(template: any) {
  const title = template.title
  let msg: string | undefined = undefined
  if (isEmpty(title)) {
    msg = 'Required'
  } else if (size(title) > 255) {
    msg = 'Name must be 255 characters or fewer'
  } else {
    const myTemplates = useNoteStore().noteTemplates
    each(myTemplates, existing => {
      if (
        (!template.id || template.id !== existing.id) &&
        title.toUpperCase() === trim(existing.title.toUpperCase())
      ) {
        msg = 'You have an existing template with this name. Please choose a different name.'
        return false
      }
    })
  }
  return msg
}
