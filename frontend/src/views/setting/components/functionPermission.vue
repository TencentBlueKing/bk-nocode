<template>
  <bk-table
    :data="listData"
    :outer-border="false">
    <bk-table-column width="30">
      <template slot-scope="{ $index }">
        <div class="page-name-container">
        <i class="node-folder-icon bk-icon icon-right-shape"
           v-if="!isShow[$index]"
           @click.stop="handleExpend($index,isShow[$index])"></i>
        <i class="node-folder-icon bk-icon icon-down-shape"
           v-else-if="isShow[$index]"
           @click.stop="handleExpend($index,isShow[$index])"></i>
        </div>
      </template>
    </bk-table-column>
    <bk-table-column label="页面名称" :width="190">
      <template slot-scope="{ row, $index }">
        <bk-checkbox
          ext-cls="page-name"
          @change="handleChange(localValue[$index].page_id,$index)"
          v-model="localValue[$index].page_id"
          :checked="checkedList[$index]">
          {{ row.page_name }}
        </bk-checkbox>
      </template>
    </bk-table-column>
    <bk-table-column label="功能" :width="190">
      <template slot-scope="{ row, $index }">
        <div class="system-function" v-if="isShow[$index]">
          <bk-checkbox-group v-model="localValue[$index].actions" @change="handleGroupChange($index)">
            <bk-checkbox v-for="item in row.actions" :key="item.id" :value="item.id">
              {{ item.name }}
            </bk-checkbox>
          </bk-checkbox-group>
        </div>
      </template>
    </bk-table-column>
  </bk-table>
</template>

<script>
import cloneDeep from 'lodash.clonedeep';

export default {
  name: 'FunctionPermission',
  props: {
    functionPermission: {
      type: Array,
      default: () => ([]),
    },
    value: {
      type: Array,
      default: () => ([]),
    },
  },
  data() {
    return {
      listData: cloneDeep(this.functionPermission),
      action_execute: [],
      localValue: cloneDeep(this.functionPermission).map(_ => ({
        page_id: '', name: '', actions: [],
      })),
      checkedList: new Array(cloneDeep(this.functionPermission).length).fill(false),
      isShow: new Array(cloneDeep(this.functionPermission).length).fill(true),
    };
  },
  // computed: {
  //   checkedList() {
  //     const tempCheckedList = new Array(this.listData.length).fill(false);
  //     this.localValue.map((item, index) => {
  //       if (item.actions.length === this.localValue[index].actions.length) {
  //         tempCheckedList[index] = true;
  //       }
  //     });
  //     return tempCheckedList;
  //   },
  // },
  watch: {
    functionPermission(val) {
      this.listData = val;
      if (val) {
        this.localValue = val.map(_ => ({
          page_id: '', name: '', actions: [],
        }));
        this.checkedList = new Array(val.length).fill(false);
        this.isShow = new Array(val.length).fill(true);
      }
    },
    value: {
      handler(val) {
        this.$nextTick(() => {
          this.setChecked(val);
        });
      },
      immediate: true,
      deep: true,
    },
  },
  methods: {
    handleExpend(index, value) {
      this.isShow.splice(index, 1, !value);
    },
    handleChange(val, index) {
      this.checkedList[index] = val;
      if (val) {
        this.localValue[index].actions = this.listData[index].actions.map(i => i.id);
      } else {
        this.localValue[index].actions = [];
      }
    },
    handleGroupChange($index) {
      if (this.listData[$index].actions.length === this.localValue[$index].actions.length) {
        this.checkedList[$index] = true;
      } else {
        this.checkedList[$index] = false;
      }
    },
    getData() {
      const actionExecute = [];
      this.listData.forEach((item, index) => {
        const actions = [];
        if (this.localValue[index].actions.length > 0) {
          item.actions.forEach((el, ind) => {
            if (this.localValue[index].actions.includes(el.id)) {
              actions.push({ id: el.id, name: el.name });
            }
          });
          actionExecute.push({ id: item.page_id, name: item.page_name, actions });
        }
        // item.actions.forEach((el, ind) => {
        //   if (this.localValue[index].actions.includes(el.id)) {
        //     const actions =
        //     actionExecute.push({ id: item.page_id, name: item.page_name, actions:  });
        //   }
        // });
      });
      return actionExecute;
    },
    setChecked(val) {
      this.localValue = cloneDeep(this.functionPermission).map(_ => ({
        page_id: '', name: '', actions: [],
      }));
      this.listData.forEach((item, index) => {
        val.forEach((el) => {
          if (item.page_id === el.id) {
            if (el.actions.length === item.actions.length) {
              this.checkedList[index] = true;
            }
            this.localValue[index].actions = el.actions.map(action => action.id);
          }
        });
      });
    },
  },
};
</script>

<style scoped lang="postcss">

/deep/ .bk-table {
  .bk-table-border {
    border-top: none;
  }
}

.page-name-container {
  i {
    cursor: pointer;
  }
}

.page-name {
  padding: 0 16px 16px;
  width: 190px;
  display: flex;
  flex-wrap: nowrap;

  /deep/ .bk-checkbox {
    display: inline-flex;
    flex-shrink: 0;
  }

  /deep/ .bk-checkbox-text {
    overflow: hidden;
    text-overflow: ellipsis;
    width: 160px;
    display: inline-block;
    white-space: nowrap;
    margin-right: 8px;
  }
}

.system-function {
  padding: 0 16px 16px;
}

/deep/ .bk-form-checkbox {
  margin-top: 16px;
}
</style>
