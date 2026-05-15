import axios from 'axios'
import {each} from 'lodash'
import utils from '@/api/api-utils'
import type {NoteAttachment} from '@/lib/types'
import {useContextStore} from '@/stores/context'


export async function addComment(parentId: number, parentType: string, body: string, attachments: NoteAttachment[]) {
  const args = {
    body,
    parentId,
    parentType
  }
  const contextStore = useContextStore()
  each(attachments, (attachment, index) => args[`attachment[${index}]`] = attachment)
  const data = await utils.postMultipartFormData('/api/comments/create', args)
  contextStore.broadcast('comment-added', data)
  return data
}

export async function deleteComment(parentNoteId: number, commentId: number) {
  const response = await axios.delete(`${utils.apiBaseUrl()}/api/comments/delete/${commentId}`)
  useContextStore().broadcast('comment-deleted', {
    parentId: parentNoteId,
    commentId: commentId
  })
  return response.data
}

export async function updateComment(commentId: number, body: string, attachments: NoteAttachment[], deleteAttachmentIds: number[]) {
  const args = {
    id: commentId,
    body,
    deleteAttachmentIds
  }
  const contextStore = useContextStore()
  each(attachments, (attachment, index) => args[`attachment[${index}]`] = attachment)
  const data = await utils.postMultipartFormData('/api/comments/update', args)
  contextStore.broadcast('comment-updated', data)
  return data
}
