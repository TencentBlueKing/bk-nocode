<template>
  <section v-bkloading="{ isLoading: funcDataLoading, zIndex: 2999 }" class="function-edit-page">
    <page-wrapper :title="title" :back-icon="true" @back="handleBackClick">
      <div slot="header" class="steps-container">
        <bk-steps
          v-if="!funcDataLoading"
          :controllable="true"
          :steps="steps"
          :cur-step="curStep"
          @step-changed="handleStepChange"></bk-steps>
      </div>
      <div class="function-edit-main" style="height: 100%">
        <router-view
          v-if="!funcDataLoading"
          :app-id="appId"
          :func-data="functionData"
          @select="handleSelect"
          @update="updateFuncData"></router-view>
      </div>
    </page-wrapper>
  </section>
</template>
<script>
import PageWrapper from '@/components/pageWrapper.vue';

const STEPS = [
  { id: 'functionBasic', icon: 1, title: '填写基本信息' },
  { id: 'functionFlow', icon: 2, title: '配置功能流程' },
  { id: 'functionAdvanced', icon: 3, title: '高级配置' },
];

export default {
  name: 'FunctionEditPage',
  components: {
    PageWrapper,
  },
  props: {
    appId: {
      type: String,
      default: '',
    },
    funcId: [Number, String], // 通过路由获取的为字符串
  },
  data() {
    return {
      steps: [],
      curStep: 0,
      funcDataLoading: !!this.funcId,
      functionData: {},
    };
  },
  computed: {
    title() {
      return this.funcId ? '编辑功能' : '新建功能';
    },
  },
  watch: {
    '$route.name'(val) {
      this.curStep = STEPS.find(item => item.id === val).icon;
    },
  },
  created() {
    if (this.funcId) {
      this.getFuncData();
    } else {
      this.functionData = {
        type: '',
        name: '',
        worksheet_ids: [],
        desc: '',
      };
    }
  },
  methods: {
    async getFuncData() {
      try {
        this.funcDataLoading = true;
        const res = await this.$store.dispatch('setting/getFunctionData', this.funcId);
        this.functionData = res.data;
        this.steps = res.data.type === 'DETAIL' ? STEPS.slice(0, -1) : STEPS.slice(0);
        // 详情类型功能隐藏高级配置步骤
        if (res.data.type === 'DETAIL' && this.$route.name === 'functionAdvanced') {
          this.$router.replace({ name: 'functionBasic', params: { appId: this.appId, funcId: this.funcId } });
          this.curStep = this.steps.find(item => item.id === 'functionBasic').icon;
          return;
        }
        this.curStep = this.steps.find(item => item.id === this.$route.name).icon;
      } catch (e) {
        console.error(e);
      } finally {
        this.funcDataLoading = false;
      }
    },
    handleSelect(val) {
      this.steps = val === 'DETAIL' ? STEPS.slice(0, -1) : STEPS;
    },
    handleBackClick() {
      this.$bkInfo({
        title: '此操作会导致您的编辑没有保存，确认吗？',
        type: 'warning',
        width: 500,
        confirmFn: () => {
          this.$router.push({ name: 'functionList', params: { appId: this.appId } });
        },
      });
    },
    handleStepChange(val) {
      if (!this.funcId && [2, 3].includes(val)) {
        return;
      }
      const name = STEPS.find(item => item.icon === val).id;
      this.$router.push({ name, params: { appId: this.appId, funcId: this.funcId } });
    },
    updateFuncData(data) {
      this.functionData = data;
    },
  },
};
</script>
<style lang="postcss" scoped>
/deep/ .page-header-container {
  .title-area {
    position: absolute;
    left: 0;
    top: 0;
  }
  .header-extend-area {
    margin: 0 auto;
    min-width: 658px;
  }
}
</style>
