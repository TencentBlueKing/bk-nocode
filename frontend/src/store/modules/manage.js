import ajax from '../../api/index';

export default {
  namespaced: true,
  state: {},
  mutations: {},
  actions: {
    getOperateLogList() {
    },
    // 获取系统分类列表
    getRemoteSystem({}, params) {
      return ajax.get('postman/remote_system/', { params }).then(response => response.data);
    },
    // 获取code接口
    getSystems({}, params) {
      return ajax.get('postman/remote_system/get_systems/', { params }).then(response => response.data);
    },
    // 获取API详情
    getRemoteApiDetail({}, params) {
      return ajax.get(`postman/remote_api/${params.id}/`, { params }).then(response => response.data);
    },
    // 获取API列表
    getRemoteApi({}, params) {
      return ajax.get('postman/remote_api/', { params }).then(response => response.data);
    },
    testFieldApiChoices({}, params) {
      return ajax.post('postman/remote_api/test_field_api_choices/', params).then(response => response.data);
    },
    // 获取级联字段数据源 （工单）
    getData({}, params) {
      return ajax.post(`ticket/fields/${params.id}/api_field_choices/`, params).then(response => response.data);
    },
    // 获取级联字段数据源 （工单）
    getCusTableApiData({}, params) {
      return ajax.post('ticket/fields/cus_table_api_field_choices/', params).then(response => response.data);
    },
    // 获取级联字段数据源 （流程--单据预览/字段隐藏。。。）
    getDataWorkflow({}, params) {
      return ajax.post(`postman/api_instance/${params.api_instance_id}/field_choices/`, params).then(response => response.data);
    },
    // 获取级联字段数据源 （提单）
    getDataReceipts({}, params) {
      return ajax.post('ticket/receipts/api_field_choices/', params).then(response => response.data);
    },
    // 获取已启用的系统分类列表
    getRemoteSystemActivated({}, params) {
      return ajax.get('postman/remote_system/', { params }).then(response => response.data);
    },
    // 创建分类
    postRemoteSystem({}, params) {
      return ajax.post('postman/remote_system/', params).then(response => response.data);
    },
    // 更新API
    putRemoteSystem({}, params) {
      return ajax.put(`postman/remote_system/${params.id}/`, params).then(response => response.data);
    },
    // 删除分类
    deleteRemoteSystem({}, id) {
      return ajax.delete(`postman/remote_system/${id}/`).then(response => response.data);
    },
    // 创建API
    postRemoteApi({}, params) {
      return ajax.post('postman/remote_api/', params).then(response => response.data);
    },
    // 更新API
    putRemoteApi({}, params) {
      return ajax.put(`postman/remote_api/${params.id}/`, params).then(response => response.data);
    },
    // http://dev.paas-poc.o.qcloud.com:8000/api/postman/remote_api/1/run_api/
    runRemoteApi({}, params) {
      return ajax.post(`postman/remote_api/${params.id}/run_api/`, params).then(response => response.data);
    },
    deleteApi({}, id) {
      return ajax.delete(`postman/remote_api/${id}/`).then(response => response.data);
    },
    batchDeleteApis({}, params) {
      return ajax.post('postman/remote_api/batch_delete/', params).then(response => response.data);
    },
    // 获取api列表
    getComponents({}, params) {
      return ajax.get('postman/remote_system/get_components/', { params }).then(response => response.data);
    },
    // 获取之前该字段之前的字段 http://dev.paas-poc.o.qcloud.com:8000/api/workflow/states/39/inputs/
    getRelatedFields({}, params) {
      return ajax.get(`workflow/states/${params.state}/variables/`, { params }).then(response => response.data);
    },
    // 获取会签所有条件选项
    getSignConditions({}, id) {
      return ajax.get(`workflow/states/${id}/sign_variables/`).then(response => response.data);
    },
    // 获取会签日志
    getSignLogs({}, params) {
      return ajax.get('ticket/logs/', { params }).then(response => response.data);
    },
    getApiImport({}, { fileType, data }) {
      return ajax.post(`postman/remote_api/0/imports/?file_type=${fileType}`, data).then(response => response.data);
    },
    // http://dev.paas-poc.o.qcloud.com:8000/api/sla/matrixs/priority_value/
    getPriority({}, { data }) {
      return ajax.post('sla/matrixs/priority_value/', data).then(response => response.data);
    },
    // 获取RPC数据
    getRpcData({}, params) {
      return ajax.post('postman/rpc_api/', params).then(response => response.data);
    },
    //  获取操作日志
    getOperateLog({}, params) {
      return ajax.get('project/operate_log/', { params }).then(response => response.data);
    },
    // 获取超级管理员
    getSuperAdmin({}, params) {
      return ajax.get('project/system_user/', { params }).then(response => response.data);
    },
    addSuperAdmin({}, params) {
      return ajax.post('project/system_user/operate_superuser/ ', params).then(response => response.data);
    },
    deleteSuperAdmin({}, params) {
      return ajax.post('project/system_user/operate_superuser/ ', params).then(response => response.data);
    },
    getApplication() {
      return ajax.get('project/system_user/',).then(response => response.data);
    },
    addApplicationAdmin({}, params) {
      return ajax.post('project/projects/operate_project_manager/', params).then(response => response.data);
    },
    //  应用数据管理员修改
    addApplicationDataAdmin({}, params) {
      return ajax.post('project/projects/operate_data_manager/', params).then(response => response.data);
    },
    // 获取流程中所有字段
    getWorkflowField({}, params) {
      return ajax.get(`workflow/templates/${params.id}/get_states/`, { params }).then(response => response.data);
    },
    //  获取开放应用列表
    getOpenSheetList({}, params) {
      return ajax.get('/project/project_white/', { params }).then(response => response.data);
    },
    addOpenSheetList({}, params) {
      return  ajax.post('/project/project_white/', params).then(response => response.data);
    },
    deleteOpenSheetList({}, params) {
      return  ajax.delete(`/project/project_white/${params.id}/`,).then(response => response.data);
    },
    updateOpenSheetList({}, params) {
      return  ajax.post(`/project/project_white/${params.id}/operate_white_list/`, params).then(response => response.data);
    },
  },
};
