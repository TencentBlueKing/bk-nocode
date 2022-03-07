import ajax from '../../api/index';
export default {
  namespaced: true,
  state: {},
  mutations: {},
  actions: {
    // 取关
    setAttention({}, { params, id }) {
      return ajax.post(`ticket/receipts/${id}/add_follower/`, params);
    },
    getList({}, { params }) {
      return ajax.get('/ticket/receipts/', { params }).then(response => response.data);
    },
    // 添加收藏
    addCollection({}, params) {
      return ajax.post('/page_design/collection/', params).then(response => response.data);
    },
    cancelCollection({}, params) {
      return ajax.delete('/page_design/collection/cancel_collection/', { params }).then(response => response.data);
    },
    // 获取用户收藏
    getCollectList() {
      return ajax.get('/page_design/collection/get_user_collection/').then(response => response.data);
    },
    getOrderDetails({}, params) {
      return ajax.get(`/ticket/receipts/${params.id}/`, { params }).then(response => response.data);
    },
    // 获取单据状态
    getOrderStatus({}, params) {
      return ajax.get(`/ticket/receipts/${params.id}/states/`, { params }).then(response => response.data);
    },
    getLog({}, params) {
      return ajax.get('/ticket/logs/', { params }).then(response => response.data);
    },
    // 获取节点状态列表
    getNodeList({}, params) {
      return ajax.get(`ticket/receipts/${params.id}/states/`, { params }).then(response => response.data);
    },
    // 转处理人
    proceedOrder({}, { params, id }) {
      return ajax.post(`ticket/receipts/${id}/proceed/`, params).then((response) => {
        const res = response.data;
        return res;
      });
    },
    withdrawTicket({}, id) {
      return ajax.post(`ticket/receipts/${id}/withdraw/`).then(res => res.data);
    },
    // 获取单据手动触发器
    getTicketHandleTriggers({}, { id, params }) {
      return ajax.get(`ticket/receipts/${id}/trigger_actions/`, { params }).then(res => res.data);
    },
    // 手动触发触发器
    executeHandleTriggers({ }, id) {
      return ajax.post(`trigger/actions/${id}/run/`).then(response => response.data);
    },
    getUser({}, params) {
      return ajax.get('role/types/', { params }).then(response => response.data);
    },
    getSecondUser({ }, params) {
      return ajax.get('role/users/', { params }).then(response => response.data);
    },
    // 获取组织架构内容
    getTreeInfo({}) {
      return ajax.get('gateway/usermanage/get_departments/').then(response => response.data);
    },
    getPreStates({}, { id }) {
      return ajax.get(`workflow/states/${id}/pre_states/`).then(response => response.data);
    },
    newAssignDeliver({ }, { params, id }) {
      return ajax.post(`ticket/receipts/${id}/operate/`, params).then(response => response.data);
    },
  },
};
