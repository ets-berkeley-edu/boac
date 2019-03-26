const state = {
  editingNoteId: undefined,
  newNoteMode: undefined
};

const getters = {
  editingNoteId: (state: any): number => state.editingNoteId,
  newNoteMode: (state: any): string => state.newNoteMode
};

const mutations = {
  editExistingNoteId: (state: any, id: number) => (state.editingNoteId = id),
  setNewNoteMode: (state: any, mode: string) => (state.newNoteMode = mode)
};

const actions = {
  editExistingNoteId: ({ commit }, id: number) => commit('editExistingNoteId', id),
  setNewNoteMode: ({ commit }, mode: string) => commit('setNewNoteMode', mode)
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
