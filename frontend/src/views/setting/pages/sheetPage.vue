<template>
  <div class="sheet-page" v-bkloading="{ isLoading: fieldsLoading }">
    <div v-if="typeof funcId === 'number'" class="sheet-page-container">
      <form-fields :use-fixed-data-source="true" :fields="fields"></form-fields>
    </div>
    <bk-exception v-else class="fields-empty" type="empty" scene="part"> 暂无内容，请在右侧绑定功能 </bk-exception>
  </div>
</template>
<script>
import FormFields from '@/components/form/formFields/index.vue';
export default {
  name: 'SheetPage',
  components: {
    FormFields,
  },
  props: {
    funcId: [Number, String],
  },
  data() {
    return {
      fields: [],
      fieldsLoading: false,
    };
  },
  watch: {
    funcId(val) {
      if (typeof val === 'number') {
        this.getFields();
      }
    },
  },
  created() {
    if (typeof this.funcId === 'number') {
      this.getFields();
    }
  },
  methods: {
    async getFields() {
      try {
        this.fieldsLoading = true;
        const res = await this.$store.dispatch('setting/getSheetPage', { service_id: this.funcId });
        this.fields = res.data;
      } catch (e) {
        console.log(e);
      } finally {
        this.fieldsLoading = false;
      }
    },
  },
};
</script>

<style scoped lang="postcss">
@import '../../../css/scroller.css';

.sheet-page {
  position: relative;
  margin: 24px;
  height: calc(100% - 56px);
  background: #ffffff;
  border: 1px dashed #3a84ff;
  border-radius: 2px;
  overflow: auto;
  @mixin scroller;
}
.sheet-page-container {
  position: relative;
  padding: 20px 16px;
}
.circle {
  position: absolute;
  top: -7px;
  right: -7px;
  width: 14px;
  height: 14px;
  background: #979ba5;
  border-radius: 50%;
  display: block;

  i {
    color: #fcfcfc;
    font-size: 14px;
    height: 14px;
    display: block;
    line-height: 14px;
  }
}
.form-fields {
  cursor: not-allowed;
}
.fields-empty {
  padding: 40px 0 50px;
}
</style>
