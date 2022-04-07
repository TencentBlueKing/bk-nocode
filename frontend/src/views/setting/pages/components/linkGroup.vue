<template>
<div class="link-group">
 <div class="group-title">
    <span>分组名称</span>
 </div>
  <div class="group-container">
      <span v-for=" i in 12" :key="i" v-bk-overflow-tips>新建项目</span>
  </div>
</div>
</template>

<script>
export default {
  name: 'LinkGroup',
  props: {
    value: {
      type: Object,
      default: () => ({}),
    },
    page: {
      type: Object,
      default: () => ({}),
    },
  },
};
</script>

<style scoped lang="postcss">
.link-group{
  width: 377px;
  height: 181px;
  border: 1px solid #dcdee5;
  box-shadow: 0 2px 4px 0 rgba(25,25,41,0.05);
  border-radius: 2px;
  background: #FFFFFF;
}
.group-title{
  height: 50px;
  border-bottom: 1px solid #f0f1f5;
  span{
    font-weight: 600;
    margin-left:20px ;
    font-size: 14px;
    color: #63656E;
    line-height: 50px;
  }
}
.group-container{
  display: flex;
  flex-wrap: wrap;
  span{
    display: inline-block;
    margin: 18px 0 0 24px;
    width:60px;
    white-space: nowrap;
    height: 20px;
    font-size: 12px;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}
</style>
