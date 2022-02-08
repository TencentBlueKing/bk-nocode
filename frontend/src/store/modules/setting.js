import ajax from '@/api/index.js';

export default {
  namespaced: true,
  state: {
    tempPageComponent: [],
    // 组织架构树
    departmentsTree: [],
    // 流程内引用触发器，保存流程信息
    triggerVariables: [],
    // 配置字段
    configurInfo: {},
  },
  mutations: {
    setComponent(state, playload) {
      state.tempPageComponent = playload;
    },
    setDepartmentsTree(state, playload) {
      state.departmentsTree = playload;
    },
    changeTriggerVariables(state, list) {
      state.triggerVariables = list;
    },
    changeConfigur(state, value) {
      state.configurInfo = value;
    },
  },
  actions: {
    getAppList({}, params) {
      return ajax.get('/project/projects/', { params }).then(response => response.data);
    },
    getAllApp({}, params) {
      return ajax.get('/project/projects/all/', { params }).then(response => response.data);
    },
    editApp({}, params) {
      const { key, name, color, desc, logo, project_config: projectConfig } = params;
      return ajax.put(`/project/projects/${params.key}/`, {
        key,
        name,
        color,
        desc,
        logo,
        project_config: projectConfig,
      }).then(response => response.data);
    },
    getAppDetail({}, key) {
      return ajax.get(`/project/projects/${key}/`).then(response => response.data);
    },
    createApp({}, params) {
      return ajax.post('/project/projects/', { ...params }).then(response => response.data);
    },
    deleteApp({}, params) {
      return ajax.delete(`/project/projects/${params.key}/`).then(response => response.data);
    },
    // 下架应用
    shelvesApp({}, params) {
      return ajax.put(`/project/projects/${params.key}/`, params).then(response => response.data);
    },
    releaseApp({}, params) {
      return ajax.post('/project/manager/publish/', params).then(response => response.data);
    },
    // 获取表单列表
    getFormList({}, params) {
      return ajax.get('/worksheet/sheets/', { params }).then(response => response.data);
    },
    getFormBasic({}, params) {
      return ajax.get(`/worksheet/sheets/${params.id}/`).then(response => response.data);
    },
    // 创建表单
    createForm({}, params) {
      return ajax.post('/worksheet/sheets/', params).then(response => response.data);
    },
    // 更新表单
    updateForm({}, params) {
      const { id, data } = params;
      return ajax.put(`/worksheet/sheets/${id}/`, data).then(response => response.data);
    },
    // 删除表单
    deleteForm({}, id) {
      return ajax.delete(`/worksheet/sheets/${id}/`).then(response => response.data);
    },
    // 获取表单字段列表
    getFormFields({}, formId) {
      const params = { worksheet_id: formId };
      return ajax.get('/worksheet/fields/', { params }).then(response => response.data);
    },
    // 新建表单字段
    createFormField({}, params) {
      return ajax.post('/worksheet/fields/', params).then(response => response.data);
    },
    // 更新表单字段
    updateFormField({}, params) {
      return ajax.put(`/worksheet/fields/${params.id}/`, params).then(response => response.data);
    },
    // 更新表单字段
    deleteFormField({}, id) {
      return ajax.delete(`/worksheet/fields/${id}/`).then(response => response.data);
    },
    // 获取工作表关联的功能和页面
    getRelatedFuncAndPage({}, id) {
      return ajax.get(`/worksheet/sheets/${id}/get_relate_service_page/`).then(response => response.data);
    },
    // 批量保存表单字段
    batchSaveFields({}, params) {
      return ajax.post('/worksheet/fields/batch_save/', params).then(response => response.data);
    },
    // 获取字段的校验方式
    getRegexList({}, params) {
      return ajax.get('/workflow/templates/get_regex_choice/', { params }).then(response => response.data);
    },
    // 获取第三方系统列表
    getRmoteSystem() {
      return ajax.get('/postman/remote_system/').then(response => response.data);
    },
    // 获取特定第三方系统api列表
    getSystemApis({}, params) {
      return ajax.get('/postman/remote_api/', { params }).then(response => response.data);
    },
    // 获取第三方接口数据
    getSourceData({}, params) {
      return ajax.post('/ticket/receipts/api_field_choices/', params).then(response => response.data);
    },
    // 获取功能列表
    getFunctionList({}, params) {
      return ajax.get('/service/projects/', { params }).then(response => response.data);
    },
    // 获取功能详情
    getFunctionData({}, id) {
      return ajax.get(`/service/projects/${id}/`).then(response => response.data);
    },
    // 获取是否内置服务
    getBuiltInService({}, id) {
      return ajax.get(`/service/projects/${id}/get_service_info/`).then(response => response.data);
    },
    // 创建功能
    createFunction({}, params) {
      return ajax.post('/service/projects/', params).then(response => response.data);
    },
    // 删除功能
    deleteFunction({}, id) {
      return ajax.delete(`/service/projects/${id}/`).then(response => response.data);
    },
    // 更新功能
    updateFunction({}, params) {
      return ajax.put(`/service/projects/${params.id}/`, params).then(response => response.data);
    },
    // 获取功能流程节点
    getFlowNodes({}, params) {
      return ajax.get('/workflow/states/', { params }).then(response => response.data);
    },
    // 获取节点详情数据
    getNodeDetail({}, id) {
      return ajax.get(`/workflow/states/${id}/`).then(response => response.data);
    },
    // 获取某一节点的前置节点列表
    getPreNodes({}, id) {
      return ajax.get(`workflow/states/${id}/pre_states/`).then(response => response.data);
    },
    // 创建节点
    createFlowNode({}, params) {
      return ajax.post('/workflow/states/', params).then(response => response.data);
    },
    // 更新节点
    updateFlowNode({}, params) {
      return ajax.put(`/workflow/states/${params.id}/`, params).then(response => response.data);
    },
    // 克隆节点
    cloneFlowNode({}, id) {
      return ajax.post(`/workflow/states/${id}/clone/`).then(response => response.data);
    },
    // 更新节点部分字段
    patchFlowNode({}, params) {
      return ajax.patch(`/workflow/states/${params.id}/`, params.data).then(response => response.data);
    },
    // 获取节点变量列表
    getNodeVars({}, params) {
      return ajax.get(`/workflow/states/${params.state}/variables/`, { params }).then(response => response.data);
    },
    // 获取节点字段列表
    getNodeFields({}, params) {
      return ajax.get('/workflow/fields/', { params }).then(response => response.data);
    },
    getSignNodeConditions({}, id) {
      return ajax.get(`/workflow/states/${id}/sign_variables/`).then(response => response.data);
    },
    // 添加节点字段
    createNodeField({}, params) {
      return ajax.post('/workflow/fields/', params).then(response => response.data);
    },
    // 更新节点字段
    updateNodeField({}, params) {
      return ajax.patch(`/workflow/fields/${params.id}/`, params).then(response => response.data);
    },
    // 删除节点字段
    deleteNodeField({}, id) {
      return ajax.delete(`/workflow/fields/${id}/`).then(response => response.data);
    },
    // 节点字段导入
    importNodeFields({}, params) {
      return ajax.post('/workflow/fields/import_fields_from_worksheet/', params).then(response => response.data);
    },
    // 删除节点
    deleteFlowNode({}, id) {
      return ajax.delete(`/workflow/states/${id}/`).then(response => response.data);
    },
    // 创建连线
    createLine({}, params) {
      return ajax.post('workflow/transitions/', params).then(response => response.data);
    },
    // 更新线条
    updateLine({}, params) {
      return ajax.put(`workflow/transitions/${params.id}/`, params.data).then(response => response.data);
    },
    // 删除线条
    deleteLine({}, id) {
      return ajax.delete(`workflow/transitions/${id}/`).then(response => response.data);
    },
    // 获取线条可使用变量
    getLineVars({}, id) {
      return ajax.get(`workflow/transitions/${id}/variables/`).then(response => response.data);
    },
    getLineTemplate({}, params) {
      return ajax.get('/workflow/transition_template/', { params }).then(response => response.data);
    },
    // 获取人员分组列表
    getRoleGroups({}, params) {
      return ajax.get('/role/types/', { params }).then(response => response.data);
    },
    // 获取人员分组下的具体角色
    getRoleGroupProcessors({}, params) {
      return ajax.get('/role/users/', { params }).then(response => response.data);
    },
    // 获取组织架构数据
    getOrganizations() {
      return ajax.get('gateway/usermanage/get_departments/').then(response => response.data);
    },
    // 获取功能流程连线
    getFlowLines({}, query) {
      const params = { ...query, page_size: 1000 };
      return ajax.get('/workflow/transitions/', { params }).then(response => response.data);
    },
    getApprovalNode({}, id) {
      return ajax.get(`/workflow/states/${id}/get_approve_states/`).then(response => response.data);
    },
    // 更新功能高级配置
    updateAdvancedConfig({}, params) {
      return ajax.post(`/service/projects/${params.id}/save_configs/`, { workflow_config: params.workflow_config }).then(response => response.data);
    },
    // 创建页面
    createPage({}, params) {
      return ajax.post('/page_design/page/', params).then(response => response.data);
    },
    getTreePage({}, params) {
      return ajax.get('/page_design/page/tree_view/', { params }).then(response => response.data);
    },
    // 获取页面导航
    getPage({}, params) {
      return ajax.get('/page_design/page/', { params }).then(response => response.data);
    },
    // 获取分组信息
    getGroupList({}) {
      return ajax.get('/page_design/page/tree_view/').then(response => response.data);
    },
    // 同级页面重排序
    pageDragSort({}, params) {
      const { id, data } = params;
      return ajax.put(`/page_design/page/${id}/move/`, data).then(response => response.data);
    },
    // 获取功能列表
    getFunctionBindList({}, params) {
      return ajax.get('/service/projects/all/', { params }).then(response => response.data);
    },
    // 获取表单页面
    getSheetPage({}, params) {
      return ajax.get(`/service/projects/${params.service_id}/get_service_first_state/`).then(response => response.data);
    },
    // 删除页面
    deletePage({}, params) {
      return ajax.delete(`/page_design/page/${params.id}/`, { params }).then(response => response.data);
    },
    // 更新页面
    updatePage({}, params) {
      return ajax.put(`/page_design/page/${params.id}/`, params).then(response => response.data);
    },
    //  页面组件创建
    createComponent({}, params) {
      return ajax.post('/page_design/page_component/', params).then(response => response.data);
    },
    updateComponent({}, params) {
      return ajax.put(`/page_design/page_component/${params.id}/`, params).then(response => response.data);
    },
    // 批量保存页面组件
    batchSaveComponent({}, params) {
      return ajax.post('/page_design/page_component/batch_save/', params).then(response => response.data);
    },
    // 获取页面详情
    getPageComponent({}, params) {
      return ajax.get('/page_design/page_component/', { params }).then(response => response.data);
    },
    //  获取工作表列表
    getWorkSheetList({}, params) {
      return ajax.get('/worksheet/sheets/', { params }).then(response => response.data);
    },
    // 收藏、取消收藏功能卡片
    collectFunction({}, params) {
      return ajax.post(`/service/projects/${params.id}/operate_favorite/`, params).then(response => response.data);
    },
    getUserGroup({}, params) {
      return ajax.get('/permit/user_group/', { params }).then(response => response.data);
    },
    // 添加用户组
    addUserGroup({}, params) {
      return ajax.post('/permit/user_group/', params).then(response => response.data);
    },
    // 删除用户组
    deleteUserGroup({}, params) {
      return ajax.delete(`/permit/user_group/${params.id}`,).then(response => response.data);
    },
    getUserByDepartment({}, params) {
      return ajax.get('gateway/usermanage/get_department_users/', { params }).then(response => response.data);
    },
    pathUpdateUserGroup({}, params) {
      return ajax.put(`/permit/user_group/${params.id}/`, params).then(response => response.data);
    },
    getFunctionPermission({}, params) {
      return ajax.get('/page_design/page_component/get_components_action/', { params }).then(response => response.data);
    },
    getUser({}, params) {
      return ajax.get('/gateway/bk_login/get_batch_users/', { params }).then(response => response.data);
    },
    // 获取公共触发器基础模型字段
    getTriggerTables({}, id) {
      return ajax.get(`workflow/tables/${id}/`).then(response => response.data);
    },
    // 获取响应事件列表信息
    getResponseList({}) {
      return ajax.get('/trigger/components/').then(response => response.data);
    },
    // 获取触发器列表
    getTemplateTriggers({}, params) {
      return ajax.get('trigger/triggers/', { params }).then(response => response.data);
    },
    // 删除触发器
    deleteTrigger({}, id) {
      return ajax.delete(`trigger/triggers/${id}/`).then(response => response.data);
    },
    // 引用公共触发器
    patchCloneTriggers({}, params) {
      return ajax.post('trigger/triggers/clone/', params).then(response => response.data);
    },
    // 全量修改一个触发器规则
    putTriggerRule({}, { params, id }) {
      return ajax.put(`/trigger/triggers/${id}/`, params).then(response => response.data);
    },
    // 创建一个触发器规则
    createTriggerRule({}, params) {
      return ajax.post('/trigger/triggers/', params).then(response => response.data);
    },
    getSecondUser({}, params) {
      return ajax.get('role/users/', { params }).then(response => response.data);
    },
    // 获取节点配置信息
    getConfigurInfo({}) {
      return ajax.get('workflow/templates/get_global_choices/').then(response => response.data);
    },
    // 获取触发器变量
    getTriggerVariables({}, { id, type, params }) {
      return ajax.get(`workflow/${type}/${id}/variables/`, { params }).then(response => response.data);
    },
    // 获取公共字段列表
    getTables({}, params) {
      return ajax.get('workflow/tables/', { params }).then(response => response.data);
    },
    // 通过触发器ID获取触发器创建下的所以规则
    getTriggerRules({}, params) {
      return ajax.get('/trigger/rules/', { params }).then(response => response.data);
    },
    // 通过id获取响应事件的内容
    getResponseListById({}, params) {
      return ajax.get('/trigger/action_schemas/', { params }).then(response => response.data);
    },
    createRespond({}, { id, params }) {
      return ajax.post(`trigger/triggers/${id}/create_or_update_action_schemas/`, params).then(response => response.data);
    },
    // 新一个触发器下创建多条规则
    batchTriggerCondition({}, { params, id }) {
      return ajax.post(`/trigger/triggers/${id}/create_or_update_rules/`, params).then(response => response.data);
    },
    getDataByKey({}, params) {
      return ajax.get('service/datadicts/get_data_by_key/', { params }).then(response => response.data);
    },
    // 获取组织架构内容
    getTreeInfo() {
      return ajax.get('gateway/usermanage/get_departments/').then(response => response.data);
    },
    // 获取表单外链
    getSheetLink({}, params) {
      return ajax.post('/page_design/page_component/generate_open_link/', params).then(response => response.data);
    },
    removeSheetLink({}, params) {
      return ajax.post('/page_design/page_component/clear_open_link/', params).then(response => response.data);
    },
    // 根据条件查询表单数据
    getWorksheetData({}, params) {
      return ajax.post('/engine/data/worksheet_data/', params).then(response => response.data);
    },
  },
};
