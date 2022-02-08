<template>
  <div class="list-page"
       @click="handleSelectPage"
       v-bkloading="{ isLoading: !edit&& loading ,zindex: 999 }">
     <span class="circle" @click="handleDelete" v-if="edit">
      <i class="bk-icon icon-close"></i>
      </span>
    <div class="table-config" :class="edit&&'is-active'">
      <div class="header-config">
        <div class="function-btn">
          <button-group
            :button-group="edit?btnList:buttonGroup"
            :edit="edit"
            @headerBtnClick="handleClick"
            @export="handleExport"
          >
          </button-group>
          <bk-button
            theme="default"
            title="功能按钮"
            size="small"
            icon="plus"
            @click="handleAddBtn"
            v-if="edit">
            添加功能
          </bk-button>
        </div>
        <div class="search-icon">
          <span class="filter-funnel"></span>
        </div>
      </div>
      <div class="custom-table" v-bkloading="{ isLoading: !edit&& loading }">
        <bk-table
          v-if="filedList.length!==0"
          ext-cls="table-border"
          :data="tableData"
          :size="size"
          :outer-border="false"
          :pagination="pagination"
          @page-change="handlePageChange"
          @page-limit-change="handlePageLimitChange"
          :header-border="false"
          :header-cell-style="{ background: '#fff' }">
          <bk-table-column v-for="field in filedList" :key="field.id" :label="field.name" :prop="field.key">
          </bk-table-column>
          <bk-table-column label="操作" width="200">
            <template slot-scope="{ row }">
              <bk-button
                v-if="!edit"
                theme="primary"
                style="margin-right:8px "
                @click="handleOptionClick(row,'detail')"
                text>
                详情
              </bk-button>
              <bk-button
                v-for="btn in (edit?optionList:tempOptionGroup)"
                :key="btn.key"
                theme="primary"
                style="margin-right:8px "
                :class="edit&&btn.isActive&&'isActive'"
                @click="handleOptionClick(row,btn)"
                text>
                {{ btn.name }}
              </bk-button>
              <bk-button
                v-show="edit"
                theme="primary"
                text
                icon="plus"
                @click="handleAddBtn('inline')">
              </bk-button>
            </template>
          </bk-table-column>
          <bk-table-column type="setting">
            <bk-table-setting-content
              :fields="filedList"
              :selected="filedList"
              :label-key="'name'"
              :value-key="'id'"
              @setting-change="handleSettingChange">
            </bk-table-setting-content>
          </bk-table-column>
        </bk-table>
      </div>
    </div>
  </div>
</template>

<script>
import buttonGroup from '../components/buttonGroup.vue';
import { random4 } from '@/utils/uuid.js';
import cloneDeep from 'lodash.clonedeep';
import Bus from '@/utils/bus.js';
import { getQuery } from '../../../utils/util';

export default {
  name: 'ListPage',
  components: {
    buttonGroup,
  },
  props: {
    filedList: {
      type: Array,
      default: () => [],
    },
    buttonGroup: {
      type: Array,
      default: () => [],
    },
    optionGroup: {
      type: Array,
      default: () => [],
    },
    edit: {
      type: Boolean,
      default: true,
    },
    pageId: {
      type: [Number, String],
    },
  },
  data() {
    return {
      btnList: cloneDeep(this.buttonGroup),
      settingList: cloneDeep(this.filedList),
      size: 'small',
      tableData: [{}],
      optionList: [],
      pagination: {
        current: 1,
        count: 10,
        limit: 10,
      },
      // 临时伪造数据一下编辑
      tempOptionGroup: [
        { name: '更新', value: 24, key: 'b736', isActive: true, type: 'UPDATE' },
        { name: '删除', value: 24, key: 'b732', isActive: true, type: 'DELETE' }],
      loading: false,
    };
  },
  watch: {
    buttonGroup: {
      handler(val) {
        this.btnList = val;
        // this.btnList.forEach(item => item.isActive = false);
      },
      deep: true,
    },
  },
  mounted() {
    if (this.filedList.length === 0 && this.edit) {
      this.$bkMessage({
        theme: 'primary',
        message: '请选择工作表',
      });
    }
    if (!this.edit) {
      console.log('edit');
      this.getTableList();
    }
    Bus.$on('onInput', (fromData) => {
      this.setBtnName(fromData);
    });
  },
  methods: {
    handleAddBtn(type) {
      if (type === 'inline') {
        this.optionList.forEach(item => item.isActive = false);
        this.btnList.forEach(item => item.isActive = false);
        this.optionList.push({ name: '默认', value: '', key: random4(), isActive: true });
      } else {
        this.btnList.forEach(item => item.isActive = false);
        this.btnList.push({ name: '', value: '', key: random4(), isActive: true });
      }
    },
    handleDelete() {

    },

    handleSelectBtn(btn) {
      this.optionList.forEach((item) => {
        item.isActive = false;
        if (btn.key === item.key) {
          item.isActive = true;
        }
      });
      if (!btn.value || !btn.name) {
        Bus.$emit('selectBtn', btn);
      }
    },
    setBtnName(fromData) {
      const { btnName, functionBind } = fromData;
      console.log(this.btnList);
      // this.btnList.forEach(item => item.isActive = false);
      this.optionList.forEach((item) => {
        console.log(item);
        if (item.isActive) {
          item.value = functionBind;
          item.name = btnName;
        }
      });
    },
    handleClick(item) {
      if (!this.edit) {
        this.$emit('headerBtnClick', item);
      }
    },
    handleOptionClick(row, type) {
      if (!this.edit) {
        console.log(row, type);
        this.$emit('handleOptionClick', row, type);
      }
    },
    async getTableList() {
      const params = {
        page: this.pagination.current,
        page_size: this.pagination.limit,
        page_id: Number(this.pageId),
        version_number: this.$route.params.version,
      };
      try {
        this.loading = true;
        const res = await this.$store.dispatch('application/getListData', params);
        this.tableData = res.data.items;
        this.pagination.current = res.data.page;
        this.pagination.count = res.data.count;
      } catch (e) {
        console.log(e);
      } finally {
        this.loading = false;
      }
    },
    handleExport() {
      const params = {
        page_id: Number(this.pageId),
        version_number: this.$route.params.version,
      };
      const paramsStr = getQuery(params);
      const BASE_URL = `${window.SITE_URL}api/engine/data/export_list_component_data/${paramsStr}`;
      window.open(BASE_URL);
    },
    handlePageChange(page) {
      this.pagination.current = page;
      this.getTableList();
    },
    handlePageLimitChange(limit) {
      this.pagination.limit = limit;
      this.getTableList();
    },
    handleSelectPage(e) {
      this.$emit('selectPage', e);
    },
  },
};
</script>

<style lang="postcss" scoped>
@import "../../../css/scroller.css";

.list-page {
  position: relative;
  height: 100%;

  .circle {
    position: absolute;
    top: -5px;
    right: 20px;
    width: 14px;
    height: 14px;
    background: #979BA5;
    border-radius: 50%;
    display: block;
    z-index: 5;

    i {
      color: #fcfcfc;
      font-size: 14px;
      height: 14px;
      display: block;
      line-height: 14px;
    }
  }

  .table-config {
    margin: 24px;
    padding: 20px 16px;
    border-radius: 2px;
    background: #FFFFFF;
    height: calc(100% - 56px);
    overflow: auto;
    position: relative;
    @mixin scroller;
  }

  .is-active {
    border: 1px dashed #3A84FF;
  }

  .header-config {
    height: 32px;
    width: 100%;
    display: flex;
    justify-content: space-between;
  }

  .function-btn {
    display: flex;
  }

  .isActive {
    border: 1px dashed #3a84ff;
  }

  .table-border {
    margin-top: 16px;
  }

  .search-icon {
    width: 26px;
    height: 26px;
  }

  /deep/ .bk-table {
    &::before {
      height: 0;
    }

    .bk-table-column-setting {
      border-left: none;
    }
  }
}
</style>
