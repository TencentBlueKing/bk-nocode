<template>
  <div class="manage-page-container">
    <router-view></router-view>
  </div>
</template>
<script>
export default {
  name: 'ManageHome',
};
</script>
<style lang="postcss">
.manage-page-container{
  .bk-form  {
    .bk-form-item {
      margin-top: 24px !important;
    }
  }

  .bk-dialog-body{
    .bk-form-item {
      margin-top: 0 !important;
      margin-bottom: 24px !important;
    }
  }
}

</style>
