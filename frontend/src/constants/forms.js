// 表单字段类型
export const FIELDS_TYPES = [
  {
    type: 'STRING',
    name: '单行文本',
    default: '',
    comp: 'Input',
  },
  {
    type: 'TEXT',
    name: '多行文本',
    default: '',
    comp: 'Textarea',
  },
  {
    type: 'INT',
    name: '数字',
    default: 0,
    comp: 'Int',
  },
  {
    type: 'DATE',
    name: '日期',
    default: '',
    comp: 'Date',
  },
  {
    type: 'DATETIME',
    name: '时间',
    default: '',
    comp: 'Datetime',
  },
  // {
  //   type: 'DATETIMERANGE',
  //   name: '时间间隔',
  // },
  {
    type: 'TABLE',
    name: '表格',
    default: [],
    comp: 'Table',
  },
  // {
  //   type: 'CUSTOMTABLE',
  //   name: '自定义表格',
  //   default: [],
  //   comp: 'CustomTable',
  // },
  {
    type: 'SELECT',
    name: '单选下拉框',
    default: '',
    comp: 'Select',
  },
  {
    type: 'INPUTSELECT',
    name: '可输入单选下拉框',
    default: '',
    comp: 'InputSelect',
  },
  {
    type: 'MULTISELECT',
    name: '多选下拉框',
    default: [],
    comp: 'MultiSelect',
  },
  {
    type: 'CHECKBOX',
    name: '复选框',
    default: [],
    comp: 'Checkbox',
  },
  {
    type: 'RADIO',
    name: '单选框',
    default: '',
    comp: 'Radio',
  },
  {
    type: 'MEMBER',
    name: '单选人员选择',
    default: [],
    comp: 'Member',
  },
  {
    type: 'MEMBERS',
    name: '多选人员选择',
    default: [],
    comp: 'Members',
  },
  {
    type: 'RICHTEXT',
    name: '富文本',
    default: '',
    comp: 'RichText',
  },
  {
    type: 'FILE',
    name: '附件上传',
    default: '',
    comp: 'Upload',
  },
  {
    type: 'IMAGE',
    name: '图片上传',
    default: '',
    comp: 'ImageFile',
  },
  // {
  //   type: 'TREESELECT',
  //   name: '树形选择',
  //   default: [],
  //   comp: 'Tree',
  // },
  {
    type: 'LINK',
    name: '链接',
    default: '',
    comp: 'Link',
  },
  {
    type: 'AUTO-NUMBER',
    name: '自动编号',
    default: '',
    comp: 'AutoNumber',
  },
  {
    type: 'DESC',
    name: '描述文本',
    default: '',
    comp: 'Description',
  },
  {
    type: 'FORMULA',
    name: '计算控件',
    default: '',
    comp: 'Formula',
  },
  // {
  //   type: 'CUSTOM-FORM',
  //   name: '自定义表单',
  //   comp: 'CustomForm',
  // },
];


export const FIELDS_REQUIRE = [
  {
    id: 'OPTION',
    name: '可选',
  },
  {
    id: 'REQUIRE',
    name: '必填',
  },
];

// 字段数据源配置
export const FIELDS_SOURCE_TYPE = [
  {
    id: 'CUSTOM',
    name: '自定义数据',
  },
  {
    id: 'API',
    name: '接口数据',
  },
  {
    id: 'WORKSHEET',
    name: '表单数据',
  },
];

// 需要展示默认值的字段类型
export const FIELDS_SHOW_DEFAULT_VALUE = ['CHECKBOX', 'RADIO', 'MEMBER', 'MEMBERS', 'RICHTEXT', 'DESC'];
// 流程配置需要展示默认值的字段类型
export const FIELDS_SHOW_DEFAULT_VALUE_IN_WORKFLOW = ['STRING', 'TEXT', 'INT', 'DATE', 'DATETIME', 'SELECT', 'MULTISELECT', 'INPUTSELECT', 'CHECKBOX', 'RADIO', 'MEMBER', 'MEMBERS', 'RICHTEXT', 'DESC'];
// 列表页面配置数据筛选规则需要过滤的字段
export  const FIELDS_FILTER_CONFIG = ['TABLE', 'LINK', 'IMAGE', 'FILE', 'RICHTEXT'];
// 默认值可以配置固定值和数据联动的字段类型  'SELECT', 'MULTISELECT', 'INPUTSELECT'
export const FIELDS_SHOW_CONFIG_VALUE = ['STRING', 'TEXT', 'INT', 'DATE', 'DATETIME'];
// 可以联动的字段
export const FIELDS_CONDITION_VALUE = ['STRING', 'TEXT', 'INT', 'DATE', 'DATETIME', 'SELECT', 'MULTISELECT', 'INPUTSELECT', 'AUTO-NUMBER'];
// 需要展示数据源的字段类型
export const FIELDS_SHOW_DATA_SOURCE = ['SELECT', 'MULTISELECT', 'INPUTSELECT', 'CHECKBOX', 'RADIO', 'TABLE', 'TREESELECT'];

// 只支持全行展示的字段类型
export const FIELDS_FULL_LAYOUT = ['TABLE', 'CUSTOMTABLE', 'RICHTEXT', 'DESC'];

// 条件关系
export const CONDITION_RELATIONS = [
  { id: '==', name: '等于' },
  { id: '!=', name: '不等于' },
  { id: '>', name: '大于' },
  { id: '<', name: '小于' },
  { id: '>=', name: '大于等于' },
  { id: '<=', name: '小于等于' },
  { id: 'in', name: '包含' },
  { id: 'not_in', name: '不包含' },
];

// 自动编号控件规则
export const AUTO_NUMBER_RULES = [
  { type: 'number', name: '流水号' },
  { type: 'datetime', name: '创建时间' },
  { type: 'field', name: '本表字段' },
  { type: 'const', name: '自定义字符' },
];

// 配置编号规则创建时间选项
export const RULE_CREATE_TIME = [
  { id: 'YYYY-MM-DD', name: '年-月-日' },
  { id: 'YYYY-MM', name: '年-月' },
  { id: 'YYYY', name: '年' },
  { id: 'MM-DD', name: '月-日' },
];

// 计算控件的内置公式
export const CALCULATION_FORMULA = [
  { key: 'SUM', name: '求和' },
  { key: 'MAX', name: '最大值' },
  { key: 'MIN', name: '最小值' },
  { key: 'CUSTOM', name: '自定义' },
  { key: 'AVERAGE', name: '平均值' },
  { key: 'PRODUCT', name: '乘积' },
  { key: 'COUNT', name: '计数' },
  { key: 'MEDIAN', name: '中位數' },
  { key: 'ARGMAX', name: '众数' },
];
// 开始/结束 日期系统默认数据源
export const DEAFAULT_TIME = [
  { key: 'create_at', name: '创建日期' },
  { key: 'update_at', name: '最近更新日期' },
  { key: 'custom', name: '指定日期' },
];
// 计算组件日期组件的精确度
export const ACCURACY_TIME = [
  { key: 'day', name: '天数' },
  { key: 'hour', name: '小时' },
  { key: 'minute', name: '分钟' },
];


