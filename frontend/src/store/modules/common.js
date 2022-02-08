import ajax from '@/api/index.js';

export default {
  namespaced: true,
  state: {},
  mutations: {},
  actions: {
    uploadFile({}, params) {
      return ajax.post('/misc/upload_file/', params).then(response => response.data);
    },
  },
};
