import _ from 'lodash';
import axios from 'axios';
import store from '@/store';
import utils from '@/api/api-utils';
import Vue from 'vue';

export function getNote(noteId) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/note/${noteId}`)
    .then(response => response.data, () => null);
}

export function markRead(noteId) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/notes/${noteId}/mark_read`)
    .then(response => response.data, () => null);
}

export function createNote(
    isBatchMode: boolean,
    sids: any,
    subject: string,
    body: string,
    topics: string[],
    attachments: any[],
    cohortIds: number[],
    curatedGroupIds: number[]
) {
  const data = {isBatchMode, sids, subject, body, topics, cohortIds, curatedGroupIds};
  _.each(attachments || [], (attachment, index) => data[`attachment[${index}]`] = attachment);
  return utils.postMultipartFormData('/api/notes/create', data).then(data => {
    const sid = store.getters['studentEditSession/sid'];
    if (sid) {
      // Non-nil 'sid' means current_user is viewing /student page.
      if (isBatchMode) {
        const noteId = data[sid];
        if (noteId) {
          // Student in view was one of sids in batch-note creation.
          getNote(noteId).then(note => {
            Vue.prototype.$eventHub.$emit('advising-note-created', note);
          });
        }
      } else if (!isBatchMode) {
          if (data.sid === sid) {
            // New note was created for student in view. In this case, the response data is the note.
            Vue.prototype.$eventHub.$emit('advising-note-created', data);
          }
      }
    }
    return data;
  });
}

export function updateNote(
    noteId: number,
    subject: string,
    body: string,
    topics: string[],
    newAttachments: any[],
    deleteAttachmentIds: number[]
) {
  const data = {
    id: noteId,
    subject: subject,
    body: body,
    topics: topics,
    deleteAttachmentIds: deleteAttachmentIds || []
  };
  _.each(newAttachments || [], (attachment, index) => data[`attachment[${index}]`] = attachment);
  return utils.postMultipartFormData('/api/notes/update', data);
}

export function deleteNote(noteId: number) {
  return axios
    .delete(`${utils.apiBaseUrl()}/api/notes/delete/${noteId}`)
    .then(response => response.data);
}

export function getTopics() {
  return axios
    .get(`${utils.apiBaseUrl()}/api/notes/topics`)
    .then(response => response.data);
}

export function addAttachment(noteId: number, attachment: any) {
  const data = {
    'attachment[0]': attachment,
  };
  return utils.postMultipartFormData(`/api/notes/${noteId}/attachment`, data);
}

export function removeAttachment(noteId: number, attachmentId: number) {
  return axios
    .delete(`${utils.apiBaseUrl()}/api/notes/${noteId}/attachment/${attachmentId}`)
    .then(response => response.data);
}
