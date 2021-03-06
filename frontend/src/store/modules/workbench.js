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
  },
};
