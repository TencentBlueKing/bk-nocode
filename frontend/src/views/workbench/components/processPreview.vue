<template>
  <div class="flow-container" v-bkloading="{ isLoading: flowDataLoading }">
    <flow-canvas
      v-if="!flowDataLoading"
      :nodes="flowData.nodes"
      :show-palette="false"
      :show-tool="false"
      :lines="flowData.lines"
      :editable="false"
      :flow-id="flowId">
    </flow-canvas>
  </div>
</template>

<script>
import FlowCanvas from '@/components/flowCanvas/index.vue';

export default {
  name: 'ProcessPreview',
  components: {
    FlowCanvas,
  },
  props: {
    flowId: [String, Number],
    nodeList: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      flowData: { nodes: [], lines: [] },
      createTicketNodeId: '',
      flowDataLoading: false,
    };
  },
  created() {
    this.getFlowData();
  },
  methods: {
    // 获取流程图详情
    async getFlowData() {
      try {
        this.flowDataLoading = true;
        const params = { workflow: this.flowId };
        const res = await Promise.all([
          this.$store.dispatch('application/getFlowNodes', params),
          this.$store.dispatch('application/getFlowLines', params),
        ]);
        this.flowData = {
          nodes: res[0].data,
          lines: res[1].data.items,
        };
        this.createTicketNodeId = res[0].data.find(item => item.is_first_state && item.is_builtin).id;
        this.flowData.nodes.forEach((item) => {
          this.$set(item, 'status', '');
          const tempNode = this.nodeList.find(node => item.id === node.state_id);
          if (tempNode) {
            item.status = tempNode.status;
          }
        });
      } catch (e) {
        console.error(e);
      } finally {
        this.flowDataLoading = false;
      }
    },
  },
};
</script>

<style scoped lang="postcss">
.flow-container {
  width: 100%;
  height: 748px;
}
</style>
