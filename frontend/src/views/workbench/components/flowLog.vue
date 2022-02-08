<template>
  <div class="flow-log" v-bkloading="{ isLoading: loading }">
    <span class="title">
      流转日志
    </span>
    <bk-timeline ext-cls="log-time-line" :list="list">
    </bk-timeline>
  </div>
</template>

<script>
import { errorHandler } from '@/utils/errorHandler';

export default {
  name: 'FlowLog',
  data() {
    return {
      loading: false,
      list: [],
      flowStartText: '流程开始',
    };
  },
  mounted() {
    this.getOperationLogList();
  },
  methods: {
    getOperationLogList() {
      const { id } = this.$route.params;
      if (!id) {
        return;
      }
      this.loading = true;
      const params = {};
      params.ticket = id;
      // params.ticket = 1;
      if (this.$route.query.token) {
        params.token = this.$route.query.token;
      }
      this.$store.dispatch('workbench/getLog', params).then((res) => {
        this.list = [];
        res.data.forEach((item) => {
          const line = {};
          line.content = item.message;
          line.tag = item.operate_at;
          if (item.message !== this.flowStartText) {
            item.content = item.operate_at;
            item.tag = item.message;
            item.type = 'primary';
            item.showMore = false;
            this.list.push(JSON.parse(JSON.stringify(item)));
          }
        });
      })
        .catch((res) => {
          errorHandler(res, this);
        })
        .finally(() => {
          this.loading = false;
        });
    },

  },
};
</script>

<style lang="postcss" scoped>
@import "../../../css/scroller.css";
.flow-log {
  margin: 24px 0 24px;
  width: 296px;
  height: calc(100% - 200px);
  //min-height: 548px;
  @mixin scroller;
  overflow-y: scroll;
  background: #FFFFFF;
  box-shadow: 0 2px 4px 0 rgba(25, 25, 41, 0.05);
  border-radius: 2px;

  .title {
    margin: 10px 0 0 24px;
    display: inline-block;
    width: 56px;
    height: 22px;
    font-family: MicrosoftYaHei;
    font-size: 14px;
    color: #313238;
    letter-spacing: 0;
    line-height: 22px;
  }

  .log-time-line {
    margin: 24px 0 0 24px;
    /deep/ .bk-timeline-title{
      height: 19px;
      font-family: MicrosoftYaHei;
      font-size: 14px;
      color: #63656E;
      letter-spacing: 0;
      text-overflow: ellipsis;
      word-wrap: break-word;
      word-break: break-word;
      padding-right: 10px;
    }
    /deep/ .bk-timeline-content{
      height: 16px;
      font-family: MicrosoftYaHei;
      font-size: 12px;
      color: #979BA5;
      letter-spacing: 0;
    }
  }

}
</style>
