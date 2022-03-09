<template>
  <div class="trigger-container">
    <div @click="showMoreConfig = !showMoreConfig" class="more-configuration" v-if="origin!=='workflow'">
      <span>高级配置</span>
      <i v-if="!showMoreConfig" class="bk-icon icon-angle-double-up"></i>
      <i v-else class="bk-icon  icon-angle-double-down"></i>
    </div>
    <div v-if="showMoreConfig"
         :class="origin!=='workflow'?
         'common-section-card-block'
         :'common-section-card-node-block'">
      <label class="common-section-card-label" v-if="origin!=='workflow'">
        触发器
      </label>
      <div class="common-section-card-body">
        <template v-if="showMoreConfig">
          <collapse-transition>
            <div>
              <!-- 触发器列表 -->
              <div>
                <ul class="bk-trigger-content">
                  <li v-for="(item, index) in boundTriggerList" :key="index" @click.stop="openNew('add', item)"
                      :class="{ 'li-transition': origin === 'transition' }">
                                        <span class="bk-trigger-icon">
                                            <i class="custom-icon-font icon-info-circle" :class="[item.iconKey]"
                                               style="font-size: 16px"></i>
                                        </span>
                    <span class="bk-trigger-name" :title="item.name" v-bk-overflow-tips="{ content: item.name }">{{ item.name || '--' }}
                                            <span v-if="item.is_draft"
                                                  style="color: #3A84FF;">草稿</span>
                                             </span>
                    <span class="bk-trigger-delete">
                                            <i class="bk-icon icon-delete" @click.stop="delTrigger(item)"></i>
                                        </span>
                  </li>
                    <div class="bk-trigger-add" slot="dropdown-trigger" title="添加触发器" @click="openNew('add')">
                      <i class="bk-icon icon-plus"></i>
                    </div>
                </ul>
              </div>
            </div>
          </collapse-transition>
        </template>
      </div>
    </div>
    <!--新建触发器-->
    <bk-sideslider
      :transfer="true"
      :is-show.sync="triggerSliderInfo.isShow"
      :title="triggerSliderInfo.title"
      :width="triggerSliderInfo.width">
      <div slot="content" style="min-height: 300px;">
        <add-trigger
          v-if="triggerSliderInfo.isShow"
          :node-type="nodeType"
          :trigger-info="triggerSliderInfo.item"
          :origin-info-to-trigger="originInfoToTrigger"
          @closeTrigger="triggerSliderInfo.isShow = false"
          @getList="getBoundTriggerList"
        ></add-trigger>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
import addTrigger from './addTrigger.vue';
import { errorHandler } from '@/utils/errorHandler';
import CollapseTransition from '@/utils/collapse-transition';

export default {
  name: 'CommonTrigger',
  components: {
    CollapseTransition,
    addTrigger,
  },
  props: {
    sourceId: {
      type: [String, Number],
      default: '',
    },
    stepSignal: {
      type: String,
      default: '',
    },
    origin: {
      type: String,
      default: 'task',
    },
    sender: {
      type: [Number, String],
      default: '',
    },
    templateStage: {
      type: String,
      default: '',
    },
    table: {
      type: [Number, String],
      default: '',
    },
    nodeType: {
      type: String,
      default: '',
    },
    node: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      boundTriggerList: [],
      boundListLoading: false,
      showMoreConfig: false,
      triggerDialogInfo: {
        isShow: false,
        searchKey: '',
        list: [],
        listLoading: false,
      },
      originInfoToTrigger: {},
      triggerSliderInfo: {
        isShow: false,
        title: '创建触发器',
        width: 950,
        addLoading: false,
        item: {},
      },
      // icon数据
      iconList: [
        { key: 'icon-notice', name: '消息', typeName: 'message' },
        { key: 'icon-user', name: '修改处理人', typeName: 'user' },
        { key: 'icon-status', name: '修改状态', typeName: 'status' },
        { key: 'icon-api', name: 'api接口', typeName: 'api' },
      ],
      // 保存任务、节点、流程区别信息
      stage: '',
      signal: '', // 信号
      type: '',
      sourceType: '',
      senderId: '',
      triggerEventListFilter: '',
    };
  },
  computed: {
    citeList() {
      return this.triggerDialogInfo.list.filter(trigger => trigger.checked);
    },
    globalChoise() {
      const tempObj = this.$store.state.setting.configurInfo;
      return Object.keys(tempObj).length > 0 ? tempObj : JSON.parse(sessionStorage.getItem('globalInfo'));
    },
    openFunction() {
      return this.$store.state.openFunction;
    },
    // 当前分类下的所有信号
    allSignal() {
      const SIGNAL_MAP = {
        state: 'STATE',
        transition: 'TRANSITION',
        workflow: 'FLOW',
      };
      // task
      if (this.stepSignal) {
        return this.stepSignal;
      }
      if (SIGNAL_MAP[this.origin]) {
        return Object.keys(this.globalChoise.trigger_signals[SIGNAL_MAP[this.origin]]).join(',');
      }
      return '';
    },
  },
  async mounted() {
    await this.initData();
  },
  methods: {
    async initData() {
      this.initParams();
      this.setFilterSignal();
      await this.getBoundTriggerList();
    },
    initParams() {
      this.senderId = this.sourceId;
      this.sourceType = 'workflow';
      // 任务模板配置
      if (this.stepSignal) {
        this.sourceType = 'task';
        this.triggerEventListFilter = 'TASK';
        this.type = 'task_schemas';
        this.stage = this.templateStage;
        return;
      }
      // 节点
      if (this.origin === 'state') {
        this.triggerEventListFilter = 'STATE';
        this.senderId = this.sender;
        this.type = 'states';
      }
      // 线条
      if (this.origin === 'transition') {
        this.showMoreConfig = true;
        this.triggerEventListFilter = 'TRANSITION';
        this.senderId = this.sender;
        this.type = 'transitions';
      }
      // 创建流程
      if (this.origin === 'workflow') {
        this.showMoreConfig = true;
        this.triggerEventListFilter = 'FLOW';
        this.type = 'templates';
      }
    },
    setFilterSignal(condition = []) {
      let conditions = condition;
      if (
        ['TASK', 'TASK-SOPS', 'SIGN'].indexOf(this.nodeType) > -1
        && this.origin === 'state'
      ) { // 根据节点类型过滤
        conditions = Array.from(new Set(['CLAIM_STATE', 'DELIVER_STATE', 'DISTRIBUTE_STATE', ...condition]));
      }
      const signalList = this.allSignal.split(',');
      this.signal = signalList.filter(key => conditions.indexOf(key) === -1).join(',');
    },
    async getBoundTriggerList() {
      if (!this.sourceId) {
        return;
      }
      const params = {
        source_id: this.sourceId,
        source_type: this.sourceType,
        sender: this.node.id,
        signal__in: this.signal,
        project_key: this.$route.params.appId,
      };
      this.boundListLoading = true;
      await this.$store.dispatch('setting/getTemplateTriggers', params).then((res) => {
        this.boundTriggerList = res.data.map(trigger => ({
          ...trigger,
          iconKey: this.iconList.find(icon => icon.typeName === trigger.icon).key,
        }));
      })
        .catch((res) => {
          errorHandler(res, this);
        })
        .finally(() => {
          this.showMoreConfig = Boolean(this.boundTriggerList.length) || this.origin === 'workflow' || this.origin === 'transition';
          this.boundListLoading = false;
        });
    },
    openNew(type, item = {}) {
      this.originInfoToTrigger = {
        id: this.sourceId,
        signal: this.signal,
        sender: this.node.id,
        filter: this.triggerEventListFilter,
        source: this.sourceType,
        type: this.type,
        stage: this.stage,
      };
      this.triggerSliderInfo.item = item;
      this.triggerSliderInfo.isShow = true;
    },
    // 删除触发器
    delTrigger(trigger) {
      this.$bkInfo({
        type: 'warning',
        title: '确认删除触发器',
        subTitle: '一旦删除，该触发器相关的动作将会一并删除。',
        confirmFn: () => {
          this.doDelTrigger(trigger);
        },
      });
    },
    doDelTrigger(trigger) {
      this.$store.dispatch('setting/deleteTrigger', trigger.id).then(() => {
        this.$bkMessage({
          message: '删除成功',
          theme: 'success',
        });
      })
        .catch((res) => {
          errorHandler(res, this);
        })
        .finally(() => {
          this.getBoundTriggerList();
        });
    },
    citeTrigger() {
      const params = {
        src_trigger_ids: this.citeList.map(item => item.id),
        dst_source_id: this.sourceId,
        dst_source_type: this.sourceType,
        dst_sender: this.senderId,
      };
      this.$store.dispatch('setting/patchCloneTriggers', params).then((res) => {
        this.$bkMessage({
          message: '引用成功',
          theme: 'success',
        });
      })
        .catch((res) => {
          errorHandler(res, this);
        })
        .finally(() => {
          this.triggerDialogInfo.isShow = false;
          this.getBoundTriggerList();
        });
    },
  },
};
</script>

<style scoped lang="postcss">
@import "../../../../../css/clearfix.css";

.trigger-container {
  margin: 24px 0;
}

.more-configuration {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #3a84ff;
  cursor: pointer;
  span {
    font-size: 14px;
  }

  .bk-icon {
    padding: 0 5px;
    margin-right: 6px;
    display: inline-block;
    font-size: 18px;

  }
}
common-section-card-node-block {
  background: #ffffff;
}
.common-section-card-block {
  margin-top: 16px;

  .common-section-card-label {
    height: 22px;
    font-size: 14px;
    color: #63656E;
    line-height: 22px;
    .common-section-card-desc {
      margin-top: 4px;
      width: 120px;
      font-size: 12px;
      color: #979ba5;
      line-height: 16px;
      word-break: break-all;
    }
  }

  .common-section-card-body {
    flex: 1;
  }
}

.bk-trigger-add {
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 48px;
  color: #979ba5;
  font-size: 32px;
  text-align: center;
  cursor: pointer;
  width: 32px;
  height: 32px;
  background: #FFFFFF;
  border: 1px solid #C4C6CC;
  border-radius: 2px;
  i{
    font-size: 20px;
  }
  &.large {
    width: 60px;
    height: 60px;
    line-height: 60px;
  }

  &:hover {
    color: #3a84ff;
    border-color: #3a84ff;
  }
}

.bk-trigger-content {
  margin-top: 10px;
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  @mixin clearfix;

  .li-transition {
    width: calc(50% - 22px) !important;
  }

  & > li {
    display: flex;
    align-items: center;
    float: left;
    margin-right: 10px;
    margin-bottom: 20px;
    line-height: 50px;
    width: 111px;
    height: 32px;
    background: #FFFFFF;
    border: 1px solid #C4C6CC;
    border-radius: 2px 0 0 2px;
    border-left: none;
    @mixin clearfix;

    &:hover {
      border-color: #3A84FF;
      cursor: pointer;
      .bk-trigger-icon {
        color: #fff;
        width: 31px;
        height: 32px;
        line-height: 31px;
        background-color: #3A84FF;
        text-align: center;
      }

      .bk-trigger-delete {
        display: block;
        color: #3A84FF;
      }
    }
  }

  .bk-trigger-icon {
    float: left;
    color: #979BA5;
    text-align: center;
    width: 31px;
    height: 32px;
    line-height: 31px;
    background: #FFFFFF;
    border: 1px solid #C4C6CC;
    border-radius: 2px 0 0 2px;
  }

  .bk-trigger-name {
    padding-left: 4px;
    text-overflow: ellipsis;
    overflow: hidden;
    width: 60px;
    height: 20px;
    font-size: 12px;
    color: #63656E;
    letter-spacing: 0;
    line-height: 20px;
    text-align: center;
    white-space: nowrap;
    display: inline-block;
  }

  .bk-trigger-delete {
    display: none;
    float: left;
    cursor: pointer;
    margin-left: 15px;
    font-size: 16px;
  }
}
</style>
