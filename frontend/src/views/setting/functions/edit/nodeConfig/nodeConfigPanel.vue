<template>
  <div class="node-config-panel" v-bkloading="{ isLoading: nodeDetailLoading }">
    <div class="header-wrapper">
      {{ typeName }}
      <i class="bk-icon icon-close back-to-flow-btn" @click="handleClose"></i>
    </div>
    <div class="config-form-wrapper">
      <div class="form-content-area">
        <bk-form ref="configForm" form-type="vertical" :rules="rules" :model="{ name }">
          <bk-form-item label="节点名称" property="name" error-display-type="normal" :required="true">
            <bk-input v-model="name" :disabled="!editable"></bk-input>
          </bk-form-item>
          <bk-form-item v-if="nodeDetail.type !== 'DATA-PROC' && funcType !== 'DETAIL'" label="处理人" :required="true">
            <processors
              ref="processorForm"
              v-model="processorData"
              :editable="editable"
              :app-id="appId"
              :flow-id="flowId"
              :node-id="nodeId"
              :exclude-list="nodeDetail.type === 'APPROVAL' ? ['OPEN'] : []"
              :disable-type="nodeDetail.type === 'SIGN'">
            </processors>
          </bk-form-item>
        </bk-form>
        <component
          ref="nodeForm"
          :is="formCompDict[nodeDetail.type]"
          :node="nodeDetail"
          :app-id="appId"
          :func-id="funcId"
          :flow-id="flowId"
          :func-type="funcType"
          :related-form="relatedForm"
          :processors="processorData.processors"
          :create-ticket-node-id="createTicketNodeId"
          :editable="editable"
          :disable-create-field="disableCreateField"
          @updateFieldIds="nodeDetail.fields = $event"
          @change="handleNodeFormChange">
        </component>
        <common-trigger
          v-if="Object.keys(nodeDetail).length>0"
          :origin="'state'"
          :node-type="funcType"
          :source-id="flowId"
          :node="nodeDetail"
          :sender="funcId">
        </common-trigger>
        <div class="actions-wrapper">
          <bk-button
            theme="primary"
            :loading="savePending"
            :disabled="nodeDetailLoading || !editable"
            @click="handleSaveClick">
            保存
          </bk-button>
          <bk-button @click="handleClose">取消</bk-button>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import cloneDeep from 'lodash.clonedeep';
import { NODE_TYPE_LIST } from '@/constants/process.js';
import Processors from '@/components/processors.vue';
import NormalNodeForm from './normalNode.vue';
import DataProcessNodeForm from './dataProcessNode.vue';
import ApiNodeForm from './apiNode.vue';
import SignNodeForm from './signNode.vue';
import ApprovalNodeForm from './approvalNode.vue';
import commonTrigger from './commonTrigger.vue';
import { errorHandler } from '@/utils/errorHandler';

export default {
  name: 'NodeConfigPanel',
  components: {
    Processors,
    NormalNodeForm,
    DataProcessNodeForm,
    ApiNodeForm,
    SignNodeForm,
    ApprovalNodeForm,
    commonTrigger,
  },
  props: {
    nodeId: Number,
    appId: {
      type: String,
      default: '',
    },
    funcId: [Number, String],
    funcType: String,
    flowId: Number,
    relatedForm: {
      type: Array,
      default: () => [],
    },
    createTicketNodeId: Number,
    disableCreateField: {
      type: Boolean,
      default: false,
    },
    editable: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      name: '',
      nodeDetail: {},
      nodeDetailLoading: true,
      processorData: {
        type: '',
        processors: '',
      },
      savePending: false,
      formCompDict: {
        NORMAL: 'NormalNodeForm',
        'DATA-PROC': 'DataProcessNodeForm',
        TASK: 'ApiNodeForm',
        SIGN: 'SignNodeForm',
        APPROVAL: 'ApprovalNodeForm',
      },
      rules: {
        name: [
          {
            required: true,
            message: '必填项',
            trigger: 'blur',
          },
        ],
      },
    };
  },
  computed: {
    typeName() {
      if (this.nodeDetail.type) {
        return NODE_TYPE_LIST.find(item => item.type === this.nodeDetail.type).name;
      }
      return '';
    },
  },
  async created() {
    await this.getNodeDetail();
  },
  methods: {
    async getNodeDetail() {
      try {
        this.nodeDetailLoading = true;
        const res = await this.$store.dispatch('setting/getNodeDetail', this.nodeId);
        this.nodeDetail = res.data;
        const { name, processors_type: processorsType, processors } = res.data;
        this.name = name;
        this.processorData = {
          type: this.nodeDetail.type === 'SIGN' ? 'PERSON' : processorsType,
          processors: cloneDeep(processors),
        };
      } catch (e) {
        console.error(e);
      } finally {
        this.nodeDetailLoading = false;
      }
    },
    handleNodeFormChange(type, value) {
      console.log(type, value);
    },
    handleSaveClick() {
      this.$refs.configForm
        .validate()
        .then(async () => {
          let processorValid = true;
          if (this.$refs.processorForm) {
            processorValid = this.$refs.processorForm.validate();
          }
          if (!processorValid) {
            return;
          }

          const configValidate = this.$refs.nodeForm.validate;
          if (configValidate) {
            // 节点表单校验
            const result = await configValidate();
            if (result) {
              this.saveNodeConfig();
            }
          } else {
            this.saveNodeConfig();
          }
        })
        .catch(e => console.error(e));
    },
    async saveNodeConfig() {
      try {
        this.savePending = true;
        const { type: processorsType, processors } = this.processorData;
        const { type, id, fields } = this.nodeDetail;
        const params = {
          id,
          type,
          workflow: this.flowId,
          name: this.name,
          is_draft: false,
          is_terminable: false,
          delivers_type: 'EMPTY',
          distribute_type: 'PROCESS',
          processors_type: processorsType,
          processors,
          fields,
        };
        if (type === 'DATA-PROC') {
          params.extras = {
            dataManager: this.$refs.nodeForm.getData(),
          };
        } else if (type === 'APPROVAL') {
          params.is_multi = this.$refs.nodeForm.getData();
        } else if (type === 'SIGN') {
          const data = this.$refs.nodeForm.getData();
          const { isSequential, finishCondition } = data;
          params.is_multi = true;
          params.is_sequential = isSequential;
          params.finish_condition = finishCondition;
        } else if (type === 'TASK') {
          const data = this.$refs.nodeForm.getData();
          const { api_info: apiInfo, variables } = data;
          params.api_info = apiInfo;
          params.variables = variables;
        }
        await this.$store.dispatch('setting/updateFlowNode', params);
        this.$bkMessage({
          theme: 'success',
          message: '保存成功',
        });
        this.$emit('save');
      } catch (e) {
        console.error(e);
      } finally {
        this.savePending = false;
      }
    },
    handleClose() {
      this.$bkInfo({
        title: '此操作会导致您的编辑没有保存，确认吗？',
        type: 'warning',
        width: 500,
        confirmFn: () => {
          this.$emit('close');
        },
      });
    },
  },
};
</script>
<style lang="postcss" scoped>
@import '../../../../../css/scroller.css';

.node-config-panel {
  margin: 24px auto 0;
  width: 1000px;
  height: calc(100% - 48px);
  background: #ffffff;
  box-shadow: 0 2px 4px 0 rgba(25, 25, 41, 0.05);
  border-radius: 2px;
}
.header-wrapper {
  position: relative;
  padding: 0 24px;
  height: 48px;
  line-height: 48px;
  font-size: 14px;
  font-weight: bold;
  color: #63656e;
  background: #fafbfd;
  .back-to-flow-btn {
    position: absolute;
    right: 16px;
    top: 12px;
    font-size: 20px;
    font-weight: bold;
    cursor: pointer;
    &:hover {
      color: #3a84ff;
    }
  }
}
.config-form-wrapper {
  padding: 24px 0;
  height: calc(100% - 48px);
  overflow: auto;
  @mixin scroller;
  .bk-form .bk-form-item {
    margin-top: 24px;
  }
}
.form-content-area {
  margin: 0 auto;
  width: 600px;
}
.actions-wrapper {
  margin-top: 24px;
}
</style>
