/* eslint-disable */
const COLUMN_LIST = [
  {
    id: 'sn',
    label: '流程编号',
    prop: 'sn',
    width: '140',
    disabled: true,
  },
  {
    id: 'service_name',
    label: '流程名称',
    prop: 'service_name',
    width: '140',
    disabled: true,
  },
  {
    id: 'current_steps',
    label: '当前节点',
    prop: 'current_steps[0].name',
    width: '140',
  },
  {
    id: 'creator',
    label: '发起人',
    prop: 'creator',
    width: '140',
    disabled: true,
  },
  {
    id: 'create_at',
    label: '创建时间',
    minWidth: '140',
    prop: 'create_at',
  },
];
export default {
  data() {
   return{
     columnList: COLUMN_LIST.slice(1),
     settingList: COLUMN_LIST,
     statusFilters: [
       { text: '待处理', value: '待处理' },
       { text: '处理中', value: '处理中' },
       { text: '后台处理中', value: '后台处理中' },
       { text: '已完成', value: '已完成' },
       { text: '执行失败', value: '执行失败' },
     ],
     statusMap: {
       WAIT: 'wait-status',
       RUNNING: 'running-status',
       QUEUEING: 'running-status',
       FINISHED: 'finish-status',
       FAILED: 'fail-status',
     },
     project_key:'',
     appList:[]
   }
  },
  created() {
    this.getAppList()
  },
  methods: {
    statusFilterMethod(value, row, column) {
      const { property } = column;
      return row[property] === value;
    },
    fixedFields(id){
      return id==='sn'?'left':''
    },
    async getAppList() {
      try {
        const res = await this.$store.dispatch('setting/getAllApp');
        this.appList = res.data.filter(item => item.publish_status !== 'UNRELEASED');
      } catch (e) {
        console.error(e);
      }
    },
  },
};
