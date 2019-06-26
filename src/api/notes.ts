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
    sid: any,
    subject: string,
    body: string,
    topics: string[],
    attachments: any[]
) {
  const data = {sid, subject, body, topics};
  _.each(attachments || [], (attachment, index) => data[`attachment[${index}]`] = attachment);
  return utils.postMultipartFormData('/api/notes/create', data).then(data => {
    // Non-nil 'sid' means current_user is viewing /student page.
    const sid = store.getters['studentEditSession/sid'];
    if (data.sid === sid) {
      Vue.prototype.$eventHub.$emit('advising-note-created', data);
    }
    const uid = store.getters['user/user'].uid;
    store.dispatch('user/gaNoteEvent', {
      id: data.id,
      name: `Advisor ${uid} created a note`,
      action: 'create'
    });
    return data;
  });
}

export function createNoteBatch(
    sids: any,
    subject: string,
    body: string,
    topics: string[],
    attachments: any[],
    cohortIds: number[],
    curatedGroupIds: number[]
) {
  const data = {sids, subject, body, topics, cohortIds, curatedGroupIds};
  _.each(attachments || [], (attachment, index) => data[`attachment[${index}]`] = attachment);
  return utils.postMultipartFormData('/api/notes/batch_create', data).then(data => {
    // Non-nil 'sid' in store means current_user is viewing /student page.
    const sid = store.getters['studentEditSession/sid'];
    if (sid) {
      const noteId = data[sid];
      if (noteId) {
        // Student in view was one of sids in batch-note creation.
        getNote(noteId).then(note => {
          Vue.prototype.$eventHub.$emit('advising-note-created', note);
        });
      }
    }
    const uid = store.getters['user/user'].uid;
    store.dispatch('user/gaNoteEvent', {
      id: data.id,
      name: `Advisor ${uid} created a batch of notes`,
      action: 'batch_create'
    });
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
