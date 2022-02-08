<template>
  <section class="workbench-page-container">
    <router-view></router-view>
  </section>
</template>
<script>
export default {
  name: 'WorkbenchHome',
};
</script>
<style lang="postcss">
.bk-table{
  .bk-table-fixed-right-patch{
    display: none;
  }
}
</style>
