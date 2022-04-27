<template>
  <div class="search-info">
    <div class="bk-filter">
      <bk-form
        :label-width="200"
        form-type="vertical"
        ext-cls="dynamic-form"
        v-model="formData"
        ref="dynamicForm">
        <div class="bk-filter-line"
             v-for="item in searchList"
             :key="item.key">
          <bk-form-item
            :label="item.name"
            v-if="['DATETIME','DATE'].includes(item.type)"
            ext-cls="form-item">
            <bk-date-picker
              style="width: 100%;"
              :type="'daterange'"
              v-model="formData[item.key]"
              @clear="handleClear(item.key)">
            </bk-date-picker>
          </bk-form-item>
          <bk-form-item
            :label="item.name"
            v-else-if="showSelectionTypeList.includes(item.type)&&!['API','WORKSHEET'].includes(item.source_type)"
            ext-cls="form-item">
            <bk-select
              searchable
              :placeholder="`请选择${item.name}`"
              :multiple="['MULTISELECT','CHECKBOX'].includes(item.type)"
              v-model="formData[item.key]"
              clearable
              @clear="handleClear(item.key)"
              style="background: #fff">
              <bk-option
                v-for="option in item.choice"
                :key="option.key"
                :id="option.key"
                :name="option.name">
              </bk-option>
            </bk-select>
          </bk-form-item>
          <bk-form-item :label="item.name" v-else-if="['INT'].includes(item.type)" ext-cls="form-item">
            <bk-input :placeholder="`请输入${item.name}`"
                      clearable
                      type="number"
                      v-model="formData[item.key]"
                      @clear="handleClear(item.key)">
            </bk-input>
          </bk-form-item>
          <bk-form-item :label="item.name" v-else-if="['MEMBER'].includes(item.type)" ext-cls="form-item">
            <member-select :placeholder="`请输入${item.name}`"
                           clearable
                           type="number"
                           v-model="formData[item.key]"
                           @clear="handleClear(item.key)">
            </member-select>
          </bk-form-item>
          <bk-form-item :label="item.name" v-else ext-cls="form-item">
            <bk-input :placeholder="`请输入${item.name}`"
                      clearable
                      v-model="formData[item.key]"
                      @clear="handleClear(item.key)">
            </bk-input>
          </bk-form-item>
        </div>
      </bk-form>
      <div class="bk-filter-line">
        <bk-button :theme="'primary'" type="submit" :title="'查询'" @click="$emit('search',formData)" size="small">
          查询
        </bk-button>
        <bk-button :theme="'default'" :title="'取消'" size="small" @click="handleCancel">
          取消
        </bk-button>
      </div>
    </div>
  </div>

</template>
<script>
import Bus from '@/utils/bus.js';
import cloneDeep from 'lodash.clonedeep';
import { SHOW_SELECT_TYPE_LIST } from '@/constants/fromTypeMap.js';
import MemberSelect from '@/components/memberSelect.vue';

export default {
  name: 'ShowSearchInfo',
  components: { MemberSelect },
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
      searchList: [],
      formData: {},
      selectList: cloneDeep(this.filedList),
      isDropdownShow: false,
      showSelectionTypeList: SHOW_SELECT_TYPE_LIST,
    };
  },
  watch: {
    searchInfo: {
      handler(val) {
        if (val.length > 0) {
          const tempList = [];
          this.filedList.forEach((select) => {
            if (val.includes(select.id)) {
              tempList.push(select);
            }
          });
          this.searchList = tempList;
        }
      },
      deep: true,
      immediate: true,
    },
  },
  mounted() {
    Bus.$on('clearSearch', (item) => {
      if (this.formData[item.key]) {
        Array.isArray(this.formData[item.key]) ? this.formData[item.key] = [] : this.formData[item.key] = '';
      }
    });
  },
  methods: {
    handleClear(key) {
      delete this.formData[key];
    },
    handleCancel() {
      this.formData = {};
      this.$emit('cancel');
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
    padding-bottom: 24px;

    .dynamic-form {
      display: flex;
      flex-wrap: wrap;
      align-items: flex-end;
    }

    .bk-filter-line {
      margin: 16px 0 0 16px;
      border: 1px solid transparent;
    }


    .bk-filter-btn {
      margin: 16px 0 0 16px;
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
    }

    /deep/ .bk-dropdown-content {
      top: 10px;
    }
  }
}


</style>
