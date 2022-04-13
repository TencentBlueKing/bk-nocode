import ajax from '@/api/index.js';

export default {
  namespaced: true,
  state: {
    todoCount: '',
  },
  mutations: {
    setTodoCount(state, data) {
      state.todoCount = data;
    },
  },
  actions: {
    uploadFile({}, params) {
      return ajax.post('/misc/upload_file/', params).then(response => response.data);
    },
    getTodoCount({ commit }) {
      return ajax.get('/ticket/receipts/total_count').then((response) => {
        commit('setTodoCount', response.data.data.my_todo);
        return response.data;
      });
    },
  },
};
