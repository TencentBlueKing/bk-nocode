<template>
  <div class="search-info">
    <div class="bk-filter">
      <bk-form
        :label-width="200"
        form-type="vertical"
        ext-cls="dynamic-form"
        ref="dynamicForm">
        <draggable handle=".bk-filter-line" group="site" class="drag-container" @end="$emit('end',$event)">
          <div class="bk-filter-line"
               :class="currentIndex===index ? 'select-class':''"
               @click.stop="currentIndex=index"
               v-for="(item ,index) in searchList"
               :key="item.key">
          <span class="delete-icon">
          <i
            class="bk-icon icon-close close-circle"
            style=" font-size:14px "
            v-if="currentIndex===index"
            @click.stop="handleDelete(item,index)" />
          <span />
          <bk-form-item :label="item.name" v-if="['DATETIME','DATE'].includes(item.type)" ext-cls="form-item">
              <bk-date-picker
                :disabled="disable"
                style="width: 100%;"
                :type="'daterange'">
              </bk-date-picker>
            </bk-form-item>
            <bk-form-item :label="item.name" v-else-if="['SELECT','RADIO'].includes(item.type)" ext-cls="form-item">
              <bk-select searchable :disabled="disable" :placeholder="`请选择${item.name}`">
                <bk-option v-for="option in item.choice"
                           :key="option.key"
                           :id="option.key"
                           :name="option.name">
                </bk-option>
              </bk-select>
            </bk-form-item>
            <bk-form-item :label="item.name" v-else ext-cls="form-item">
              <bk-input :disabled="disable" :placeholder="`请输入${item.name}`">
              </bk-input>
            </bk-form-item>
        </span>
          </div>
          <div class="bk-filter-btn">
            <bk-form-item>
              <bk-dropdown-menu
                @show="dropdownShow"
                @hide="dropdownHide"
                v-if="selectList.length>0"
                ref="dropdown"
                ext-cls="dropdown">
                <div class="add-search" slot="dropdown-trigger">
                  <i class="bk-icon icon-plus"></i>
                </div>
                <ul class="bk-dropdown-list" slot="dropdown-content">
                  <li v-for="(ele,index) in selectList" :key="ele.key">
                    <a @click="triggerHandler(ele,index)">{{ ele.name }}</a>
                  </li>
                </ul>
              </bk-dropdown-menu>
            </bk-form-item>
          </div>
        </draggable>
      </bk-form>
    </div>
  </div>

</template>
<script>
import cloneDeep from 'lodash.clonedeep';
import draggable from 'vuedraggable';

const filterType = ['TABLE', 'RICHTEXT', 'FILE', 'TREESELECT', 'LINK', 'CUSTOM-FORM', 'CASCADE', 'IMAGE'];
export default {
  name: 'SearchInfo',
  components: { draggable },
  props: {
    filedList: {
      type: Array,
      default: () => [],
    },
    searchInfo: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      disable: true,
      currentIndex: -1,
      searchList: [],
      selectList: [],
      isDropdownShow: false,
    };
  },
  watch: {
    searchInfo: {
      handler(val) {
        const list = cloneDeep(this.filedList).filter(v => !filterType.includes(v.type));
        if (val.length > 0) {
          const tempList = [];
          const tempSelectList = [];
          list.forEach((select) => {
            if (!val.includes(select.id)) {
              tempSelectList.push(select);
            } else if (val.includes(select.id)) {
              tempList.push(select);
            }
          });
          this.searchList = tempList;
          this.selectList = tempSelectList;
        } else {
          this.searchList = [];
          this.selectList = cloneDeep(list);
        }
      },
      immediate: true,
    },
  },
  methods: {
    dropdownShow() {
      this.isDropdownShow = true;
    },
    dropdownHide() {
      this.isDropdownShow = false;
    },
    triggerHandler(item, index) {
      this.searchList.push(item);
      this.selectList.splice(index, 1);
      this.$emit('change', item);
    },
    handleDelete(item, index) {
      this.currentIndex = -1;
      this.searchList.splice(index, 1);
      this.selectList.push(item);
      this.$emit('delete', index);
    },
  },
};
</script>

<style scoped lang="postcss">
.search-info {
  box-sizing: content-box;
  margin-top: 8px;
  width: 100%;
  background: #F5F7FA;
  border-radius: 2px;

  .bk-filter {

    .dynamic-form {
      display: flex;
      flex-wrap: wrap;
      padding-bottom: 24px;
      align-items: flex-end;
    }

    .select-class {
      border: 1px dashed #979ba5;
      background: #EAEBF0;
      cursor: move;
    }

    .bk-filter-line {
      position: relative;
      margin: 16px 0 0 16px;
      border: 1px solid transparent;
      padding: 4px;

      .close-circle {
        position: absolute;
        top: -7px;
        right: -7px;
        height: 14px;
        width: 14px;
        background: #979ba5;
        border-radius: 50%;
        z-index: 10;
        color: #fcfcfc;
        font-size: 14px;
        display: block;
        line-height: 14px;
      }

      &:hover {
        border: 1px dashed #979ba5;
        background: #EAEBF0;
        cursor: move;
      }

      &:after {
        position: absolute;
        content: '';
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        cursor: move;
      }
    }

    .form-item {
      cursor: move;

      /deep/ .bk-label {
        font-size: 12px;
      }
    }

    .bk-filter-btn {
      margin: 16px 0 0 16px;
      padding-bottom: 2px;
    }

    .drag-container {
      display: flex;
      flex-wrap: wrap;
      align-items: flex-end;
    }
  }


  .dropdown {
    position: relative;

    .add-search {
      width: 26px;
      height: 26px;
      background: #FFFFFF;
      border: 1px solid #C4C6CC;
      border-radius: 2px;
    //margin-left: 16px; cursor: pointer;

      i {
        line-height: 24px;
        font-size: 20px;
        display: block;
      }
    }

    .bk-dropdown-list {
      cursor: pointer;
      height: 100%;
      overflow-y: auto;
    }

    /deep/ .bk-dropdown-content {
      top: 10px;
    }
  }
}


</style>
