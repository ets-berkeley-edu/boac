import {each, filter, get, isEmpty, map, size, trim} from 'lodash'
import type {
  AcademicTimelineMessage,
  Attachment,
  BoaConfig,
  BoaUser,
  DepartmentMembership,
  EForm,
  Note,
  NoteTemplate,
} from '@/lib/types'
import {getPeerAdvisorDepartmentMemberships} from '@/lib/berkeley-department'
import {isPeerAdvisorManager} from '@/lib/boa-user'
import {oxfordJoin, stripHtmlAndTrim} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

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
  let canEdit: boolean = false
  if (user.uid === note.author.uid && (!note.isPrivate || user.canAccessPrivateNotes)) {
    canEdit = true
  } else if (isPeerAdvisorManager(user) && note.peerAdvisingDepartmentId) {
    // Peer Advisor Managers can edit notes created by Peer Advisors within same Peer Advising department.
    const memberships: DepartmentMembership[] = getPeerAdvisorDepartmentMemberships(user, 'peer_advisor_manager')
    canEdit = map(memberships, 'peerAdvisingDepartmentId').includes(note.peerAdvisingDepartmentId)
  }
  return canEdit
}

export function summarizeNoteForAcademicTimeline(message: AcademicTimelineMessage, stripHtml?: boolean): string {
  let summary = message.message
  if ('note' === message.type) {
    if (message.subject) {
      summary = message.subject
    } else if (size(message.message)) {
      if (stripHtml) {
        // Notes without a subject get a pseudo-subject line using the first line of the message body.
        const cleanse = (s: string) => stripHtmlAndTrim(s).replace(/\n\r/g, ' ')
        const regex: string = ['<br>', '<br/>', '</p>', '</div>'].map(phrase => `(${phrase})`).join('|')
        const index: number = message.message.search(new RegExp(regex))
        summary = cleanse(index === -1 ? summary : summary.slice(0, index))
        summary = summary || cleanse(message.message)
      } else {
        summary = message.message
      }
    } else if (message.category) {
      summary = `${message.category}${message.subcategory ? `, ${message.subcategory}` : ''}`
    } else {
      summary = `${!isEmpty(message.author.departments) ? message.author.departments[0].deptName : ''} advisor ${message.author.name || ''}`
      if (message.topics && size(message.topics)) {
        summary += `: ${oxfordJoin(message.topics)}`
      }
    }
  } else if ('eForm' === message.type) {
    const eForm: EForm = message.eForm
    if (eForm.dataSource === 'student_cpp_change_eforms') {
      summary = `Career Program Plan eForm: ${eForm.action} – ${eForm.status}`
    } else if (eForm.dataSource === 'student_course_load_eforms') {
      summary = `Reduced Course Load eForm: ${eForm.action} – ${eForm.status}`
    } else if (eForm.dataSource === 'student_late_drop_eforms') {
      summary = `Late Change of Schedule Request eForm: ${eForm.action} – ${eForm.status}`
    } else {
      summary = `eForm: ${eForm.action} – ${eForm.status}`
    }
  } else if ('appointment' === message.type) {
    if (message.createdBy === 'Calendly') {
      summary = `${trim(message.appointmentTitle)}, with ${message.advisor.name}`
    } else if (message.appointmentTitle && message.appointmentTitle.trim().length) {
      summary = message.appointmentTitle
    } else if (message.details && message.details.trim().length) {
      summary = stripHtml ? stripHtmlAndTrim(message.details).replace(/\n\r/g, ' ') : message.details
    } else {
      summary = message.legacySource === 'SIS' ? 'Imported SIS Appt' : 'Advising Appt'
      if (get(message, 'advisor.name')) {
        summary = `${summary}: ${message.advisor.name}`
      }
    }
  }
  return summary
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
