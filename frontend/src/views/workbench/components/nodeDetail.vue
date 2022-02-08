<template>
  <div class="bk-current-node" :style="{ height: `${defaultTableHeight}px` }">
    <div class="bk-current-info" v-bkloading="{ isLoading: loading }">
      <template v-if="nodeList.length !== 0">
        <node-detail-item
          v-for="(item, index) in nodeList"
          :key="index"
          :index="index"
          :node-info="item"
          :node-list="nodeList"
          :ticket-info="basicInfomation"
          :is-last-node="index === nodeList.length - 1">
        </node-detail-item>
      </template>
      <template v-else>
        <!-- 暂无内容 -->
        <span class="ui-empty" type="empty" scene="part">{{ "您暂无任务需要处理" }}</span>
      </template>
<!--      <template>-->
<!--        &lt;!&ndash; 暂无内容 &ndash;&gt;-->
<!--        <div class="bk-no-content bk-no-status">-->
<!--          <template v-if="basicInfomation.current_status === 'TERMINATED'">-->
<!--            <p>{{ "该单据已被终止" }}</p>-->
<!--          </template>-->
<!--          <template v-else>-->
<!--            <p>{{ "该单据已结束" }}</p>-->
<!--          </template>-->
<!--        </div>-->
<!--      </template>-->
    </div>
  </div>
</template>

<script>
import nodeDetailItem from './nodeDetailItem.vue';

export default {
  name: 'NodeDetail',
  components: {
    nodeDetailItem,
  },
  props: {
    // 单据信息
    basicInfomation: {
      type: Object,
      default: () => {
      },
    },
    nodeList: {
      type: Array,
      default: () => [],
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },
  created() {
    this.defaultTableHeight = document.documentElement.clientHeight - 202 ;
  },
};
</script>

<style scoped lang='postcss'>
@import "../../../css/scroller.css";
.bk-current-node{
  padding: 20px;
  height: calc(100% - 98px);
  overflow-y: scroll;
  @mixin scroller
}

.bk-current-info {
  position: relative;
  padding: 10px;
}

.bk-current-padding {
  padding: 0;
}

.bk-no-status {
  padding: 67px 0;
  text-align: center;
  padding: 80px 0;

  img {
    width: 110px;
  }

  p {
    font-size: 16px;
    color: #63656E;
    margin-top: 10px;
  }
}

.ui-empty {
  margin: 50px auto;
}
</style>
