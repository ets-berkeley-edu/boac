import {each, filter, get, isEmpty, size, trim} from 'lodash'
import type {Attachment, BoaConfig, BoaUser, DepartmentMembership, Note, NoteTemplate} from '@/lib/types'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'
import {isPeerAdvisorManager} from '@/lib/boa-user'
import {getPeerAdvisorDepartmentMembership} from '@/lib/berkeley-department'

export function addFileDropEventListeners(): void {
  const preventFileDropOutsideFormControl = e => {
    const classList = get(e.target, 'classList', '')
    if (!classList.contains('choose-file-for-note-attachment')) {
      e.preventDefault()
      e.dataTransfer.effectAllowed = 'none'
      e.dataTransfer.dropEffect = 'none'
    }
  }
  window.addEventListener('dragenter', preventFileDropOutsideFormControl, false)
  window.addEventListener('dragover', preventFileDropOutsideFormControl)
  window.addEventListener('drop', preventFileDropOutsideFormControl)
}

export function canUserEditNote(note: Note, user: BoaUser): boolean {
  let canEdit = false
  if (note.type === 'note' && !note.legacySource) {
    if (user.uid === note.author.uid && (!note.isPrivate || user.canAccessPrivateNotes)) {
      canEdit = true
    } else if (isPeerAdvisorManager(user) && note.peerAdvisingDepartmentId) {
      // Peer Advisor Managers can edit notes created by Peer Advisors within same Peer Advising department.
      const membership: DepartmentMembership = getPeerAdvisorDepartmentMembership(user, 'peer_advisor_manager')
      canEdit = get(membership, 'peerAdvisingDepartmentId') === note.peerAdvisingDepartmentId
    }
  }
  return canEdit
}

export function validateAttachment(attachments: Attachment[], existingAttachments: Attachment[]): string | null {
  const maxAttachmentMegabytes: number = 20
  const maxAttachmentBytes: number = maxAttachmentMegabytes * 1024 * 1024
  if (!(attachments && attachments.length)) {
    return 'No attachment provided.'
  }
  const config: BoaConfig = useContextStore().config
  if (size(attachments) + size(existingAttachments) > config.maxAttachmentsPerNote) {
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

export function validateTemplateTitle(template: NoteTemplate) {
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
