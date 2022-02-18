<template>
<div class="basic-info">
<!--  <span class="title">-->
<!--    基本信息-->
<!--  </span>-->
  <div class="info-container">
    <bk-form :label-width="60">
      <bk-form-item ext-cls="custom-label" v-for="item in formData" :label="item.label" :key="item.label">
        {{item.name}}
      </bk-form-item>
    </bk-form>
  </div>
</div>
</template>

<script>
export default {
  name: 'BasicInfo',
  props: {
    basicInfo: {
      type: Object,
      default: () => {},
    },
  },
  data() {
    return {
      formData: [{
        label: '流程名称:',
        name: '',
        id: 'service_name',
      },
      {
        label: '所属应用：',
        name: '',
        id: 'relate_project',
      },
      {
        label: '发起人：',
        name: '',
        id: 'creator',
      },
      {
        label: '创建时间:',
        name: '',
        id: 'create_at',
      }],
    };
  },
  mounted() {
    this.initFormData();
  },
  methods: {
    initFormData() {
      this.formData.map((item) => {
        item.name  = this.basicInfo[item.id]  || '--';
      });
    },
  },
};
</script>

<style lang="postcss" scoped>
.basic-info{
  width: 296px;
  height: 176px;
  background: #FFFFFF;
  box-shadow: 0 2px 4px 0 rgba(25,25,41,0.05);
  border-radius: 2px;
  .title{
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
  .info-container{
    margin:16px 0 0 30px;
    .custom-label{
      height: 20px;
      font-family: MicrosoftYaHei;
      font-size: 12px;
      color: #63656E;
      letter-spacing: 0;
      line-height: 20px;
      margin-top: 0px;
      /deep/ .bk-label{
        height: 20px;
        font-family: MicrosoftYaHei;
        font-size: 12px;
        color: #979BA5;
        letter-spacing: 0;
        text-align: right;
        line-height: 20px;
        padding: 0;
      }
      /deep/ .bk-form-content{
        line-height: 20px;
        margin-left: 76px !important;
      }
    }
  }
}
</style>
