/* eslint-disable */
export default {
  data() {
   return{
     statusFilters: [
       { text: '待处理', value: '待处理' },
       { text: '处理中', value: '处理中' },
       { text: '后台处理中', value: '后台处理中' },
       { text: '已结束', value: '已结束' },
       { text: '执行失败', value: '执行失败' },
     ],
     statusMap: {
       WAIT: 'wait-status',
       RUNNING: 'running-status',
       QUEUEING: 'running-status',
       FINISHED: 'finish-status',
       FAILED: 'fail-status',
     },
   }
  },
  methods: {
    statusFilterMethod(value, row, column) {
      const { property } = column;
      return row[property] === value;
    },
  },
};
