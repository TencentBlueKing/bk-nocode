<template>
  <router-link
    class="table-link"
    :to="{ name: 'processDetail', params: { id: row.id } }">
    {{ row.sn }}
  </router-link>
</template>

<script>
export default {
  name: 'ColumnSn',
  props: {
    row: {
      type: Object,
      default: () => {},
    },
  },
};
</script>

<style scoped lang="postcss">
.table-link {
  display: inline-block;
  width: 200px;
  color: #3a84ff;
}
</style>
