<template>
  <div class="side-panel">
    <div class="panel-title">
      <span>组件库</span>
    </div>
    <div class="component-list-container">
      <div v-for="(group, index) in list" class="field-group" :key="index">
<!--        <div class="group-name">{{ group.name }}</div>-->
        <draggable
          class="list-wrap"
          handle=".component-item"
          tag="p"
          :sort="false"
          :group="{
            name: 'menu',
            pull: 'clone',
            put: false,
          }"
          :list="group.items"
          :move="handleMove"
          @end="handleEnd">
          <li v-for="field in group.items" class="component-item drag-entry" :data-type="field.type" :key="field.type">
            {{ field.name }}
          </li>
        </draggable>
      </div>
    </div>
  </div>
</template>

<script>
import { COMPONENT_TYPES }  from '@/constants/comps.js';
import draggable from 'vuedraggable';
export default {
  name: 'ComponentPanel',
  components: {
    draggable,
  },
  data() {
    return {
      list: this.getGroupedFields(),
    };
  },
  methods: {
    getGroupedFields() {
      const layOutComp = ['TAB'];
      const group = [
        {
          name: '布局组件',
          items: [],
        },
        {
          name: '门户组件',
          items: [],
        },
      ];
      COMPONENT_TYPES.forEach((item) => {
        if (layOutComp.includes(item.type)) {
          group[0].items.push(item);
        } else {
          group[1].items.push(item);
        }
      });
      return group;
    },
    handleMove() {
      this.$emit('move');
    },
    handleEnd() {
      this.$emit('end');
    },
  },
};
</script>

<style scoped lang="postcss">
.side-panel {
  position: relative;
  width: 240px;
  height: 100%;
  background: #fcfcfc;
  z-index: 1;
  box-shadow: 1px 0 0 0 #DCDEE5;
  flex-shrink: 0;
}

.panel-title {
  padding: 8px 21px;
  height: 40px;
  line-height: 40px;
  color: #313238;
  font-size: 14px;
  background: #ffffff;
  border-top: 1px solid #dcdee5;
  border-bottom: 1px solid #dcdee5;
  display: flex;
  align-items: center;
}

.component-list-container {
  margin: 16px 0 8px;
  padding: 0  16px ;
  height: calc(100% - 44px);
  overflow: auto;
}
.group-name {
  line-height: 20px;
  margin: 16px 0 8px;
  color: #c4c6cc;
  font-size: 12px;
  font-weight: normal;
}

.component-item {
  margin-bottom: 8px;
  padding: 0 4px 0 16px;
  width: 100px;
  height: 32px;
  line-height: 32px;
  font-size: 12px;
  color: #63656e;
  background: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 2px;
  cursor: move;
  user-select: none;
  &:hover {
    color: #3a84ff;
    border-color: #3a84ff;
  }
}

.list-wrap {
  display: flex;
  justify-content: space-between;
  flex-flow: row wrap;
}
</style>
