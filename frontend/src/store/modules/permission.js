import ajax from '../../api/index';

export default {
  namespaced: true,
  state: {
    permMeta: {},
  },
  mutations: {
    setPermMeta(state, data) {
      state.permMeta = data;
    },
  },
  actions: {
    // 获取权限元数据
    getPermMeta({ commit }) {
      return ajax.get('/openapi/system/meta/').then((response) => {
        commit('setPermMeta', response.data.data);
        return response.data;
      });
    },
    // 获取页面导航权限
    getPagePerm({}, params) {
      return ajax.get('/permit/query/get_page_permit/', { params }).then(response => response.data);
    },
    // 获取页面操作按钮的操作权限
    getPageActionPerm({}, params) {
      return ajax.get('/permit/query/get_action_permit/', { params }).then(response => response.data);
    },
    // 获取权限中心跳转链接
    getPermUrl({}, params) {
      return ajax.post('/iam/permission/query_apply_permission_url/', params).then(response => response.data);
    },
    // 获取平台管理权限
    getPlatform() {
      return ajax.get('/iam/permission/platform_permission/').then(response => response.data);
    },
  },
};
