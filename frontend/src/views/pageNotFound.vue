<template>
  <div class="page-not-found">
    <bk-exception class="exception-wrap" type="404">
      <span>页面不存在</span>
    </bk-exception>
  </div>
</template>
<script>
export default {
  name: 'PageNotFound',
};
</script>
<style lang="postcss" scoped>
.exception-wrap {
  margin-top: 160px;
}
</style>
