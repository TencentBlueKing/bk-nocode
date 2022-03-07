import ajax from '@/api/index.js';
export default {
  namespaced: true,
  state: {},
  mutations: {},
  actions: {
    getProject() {
      return ajax.get('/project/version/page/').then(respond => respond.data);
    },
    // 获取应用版本
    getProjectVersion({}, params) {
      return ajax.post('/project/manager/version/', { params }).then(respond => respond.data);
    },
    // 获取某个版本的页面导航配置
    getPageList({}, params) {
      return ajax.get('/project/version/page/', { params }).then(respond => respond.data);
    },
    // 获取某个版本的页面下的组件配置
    getPageConfig({}, params) {
      return ajax.get('/project/version/page_component/', { params }).then(respond => respond.data);
    },
    // 获取某个版本的项目配置
    getVersionConfig({}, params) {
      return ajax.post('/project/version/project_config/', params).then(respond => respond.data);
    },
    // 获取某个版本下的工作表配置
    getFormConfig({}, params) {
      return ajax.post('/project/version/project_config/', params).then(respond => respond.data);
    },
    // 获取工作表绑定的功能的提单字段信息
    getFormPageFields({}, params) {
      return ajax.post('/ticket/receipts/get_first_state_fields_by_post/', params).then(respond => respond.data);
    },
    //  提单
    createTicket({}, params) {
      return ajax.post('/ticket/receipts/create_ticket/', params).then(respond => respond.data);
    },
    // 获取节点
    getFlowNodes({}, params) {
      return ajax.get(`/workflow/versions/${params.workflow}/states/`, {}).then(response => response.data);
    },
    // 获取连线
    getFlowLines({}, params) {
      return ajax.get(`/workflow/versions/${params.workflow}/transitions/`, {}).then(response => response.data);
    },
    //  获取列表数据
    getListData({}, params) {
      return ajax.post(`/engine/data/list_component_data/?page_size=${params.page_size}&page=${params.page}`, params).then(response => response.data);
    },
    // 获取某个版本下的工作表下的字段信息
    getWorksheetFiledConfig({}, params) {
      return ajax.get('/project/version/worksheet_field/', { params }).then(respond => respond.data);
    },
    getCollectedCards({}, params) {
      return ajax.get('/page_design/collection/collection_of_page/', { params }).then(response => response.data);
    },
    getDetail({}, params) {
      return ajax.get('/engine/data/get_detail_data/', { params }).then(response => response.data);
    },
    // 外链通过openApi获取工作表绑定的功能的提单字段信息
    getOpenFormPageFields({}, params) {
      return ajax.get('/openapi/ticket/get_first_state_fields/', { params }).then(respond => respond.data);
    },
    //  外链通过openApi提单
    createOpenApiTicket({}, params) {
      return ajax.post('/openapi/ticket/create_ticket/', params).then(respond => respond.data);
    },
    // 导出列表组件的数据
    exportData({}, params) {
      return ajax.post('/engine/data/export_list_component_data/', params, { responseType: 'arraybuffer' }).then(respond => respond.data);
    },
    uploadFile({}, params) {
      return ajax.post('/engine/data/import_data/', params).then(response => response.data);
    },
    validateData({}, parmas) {
      return ajax.post('/engine/data/validate_data/', parmas).then(response => response.data);
    },
  },
};
