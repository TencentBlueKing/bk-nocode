<template>
  <div class="card-page">
    <div class="card-container">
      <div
        class="card-item"
        v-for="(item, index) in cards"
        :key="index"
        :style="{ 'border-color': crtIndex === index ? '#3a84ff' : '' }"
        @click="handleSelect(index)">
        <span class="delete-icon" @click.stop="handleDelete(index)">
          <i class="bk-icon icon-close"></i>
        </span>
        <func-card page-type="FUNCTION" :card="item"> </func-card>
      </div>
      <div class="add-card" @click="handleAddCard"><i class="bk-icon icon-plus"></i>新增功能卡片</div>
    </div>
  </div>
</template>

<script>
import cloneDeep from 'lodash.clonedeep';
import FuncCard from '../components/funcCard.vue';
import { funcColors } from '@/constants/colors.js';

export default {
  name: 'FunctionPage',
  components: {
    FuncCard,
  },
  props: {
    cards: {
      type: Array,
      default: () => [],
    },
    pageId: Number,
    crtIndex: Number,
  },
  methods: {
    handleAddCard() {
      const list = cloneDeep(this.cards);
      const bgColor = funcColors[list.length % funcColors.length];
      list.push({
        page_id: this.pageId,
        type: 'FUNCTION',
        value: '',
        config: { name: '', desc: '', bgColor },
      });
      this.$emit('update', list, list.length - 1);
    },
    handleDelete(index) {
      const list = cloneDeep(this.cards);
      list.splice(index, 1);
      const crtIndex = list.length - 1;
      this.$emit('update', list, crtIndex);
    },
    handleSelect(index) {
      this.$emit('update', this.cards, index);
    },
  },
};
</script>

<style scoped lang="postcss">
@import '../../../css/scroller.css';
.card-page {
  padding: 12px;
  height: 100%;
  overflow: auto;
  @mixin scroller;
}
.card-container {
  display: flex;
  flex-wrap: wrap;
}

.card-item {
  margin: 12px;
  border: 1px dashed #979ba5;
  position: relative;
  cursor: pointer;
  border-radius: 2px;
  &:hover {
    border-color: #3a84ff;
    .delete-icon {
      display: inline-block;
    }
  }
  .delete-icon {
    display: none;
    position: absolute;
    top: -7px;
    right: -7px;
    width: 14px;
    height: 14px;
    background: #979ba5;
    border-radius: 50%;
    z-index: 1;

    i {
      color: #fcfcfc;
      font-size: 14px;
      height: 14px;
      display: block;
      line-height: 14px;
    }
  }
}
.add-card {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 12px;
  width: 278px;
  height: 162px;
  color: #3a84ff;
  font-size: 14px;
  border: 1px dashed #979ba5;
  border-radius: 2px;
  cursor: pointer;
  &:hover {
    border-color: #3a84ff;
  }
  i {
    margin-right: 5px;
    font-size: 16px;
  }
}
</style>
