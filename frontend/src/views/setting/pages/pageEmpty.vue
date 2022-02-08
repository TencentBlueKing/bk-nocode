<template>
  <div class="page-empty">
    <div class="empty-content">
      <img :src="imgUrl" alt="empty" />
      <p class="tips-text">{{ text }}</p>
      <bk-button theme="primary" icon="plus" @click="$emit('createPage', id)">新增页面</bk-button>
    </div>
  </div>
</template>
<script>
export default {
  name: 'PageEmpty',
  props: {
    isGroup: {
      type: Boolean,
      default: false,
    },
    id: Number,
  },
  data() {
    return {
      imgUrl: require('@/assets/images/empty.svg'),
    };
  },
  computed: {
    text() {
      return this.isGroup ? '当前分组还没有页面哦，你可以先新增页面' : '当前还没有内容哦，你可以先新增页面';
    },
  },
};
</script>
<style lang="postcss" scoped>
.page-empty {
  width: calc(100% - 216px);
  height: 100%;
}
.empty-content {
  padding-top: 125px;
  text-align: center;
  img {
    width: 340px;
  }
}
.tips-text {
  margin-bottom: 16px;
  font-size: 16px;
  color: #63656e;
}
</style>
