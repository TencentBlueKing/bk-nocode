<template>
  <section class="function-list-page">
    <page-wrapper title="功能管理">
      <template slot="header">
        <bk-button :theme="'primary'" :title="'应用发布'" @click="onReleaseClick">
          应用发布
        </bk-button>
      </template>
      <div class="list-table">
        <div class="operate-area">
          <bk-button theme="primary" icon="plus" @click="handleCreateFunction">新建</bk-button>
          <div class="search-icon top-start" @click="isShowSearchInfo = !isShowSearchInfo" v-bk-tooltips="topStart">
            <i class="custom-icon-font icon-filter-funnel"></i>
          </div>
          <search-item @search="handleSearch" @cancel="handleCancel" v-show="isShowSearchInfo"></search-item>
          <div class="search-item-container">
            <template v-if="!isShowSearchInfo && searchInfo.length!==0">
              <search-tag v-for="item in searchInfo" :search-item="item" :key="item.key"
                          @delete="handleRemoveSearch"></search-tag>
            </template>
          </div>
        </div>
        <bk-table
          ext-cls="custom-table"
          v-bkloading="{ isLoading: listLoading }"
          :data="listData"
          :outer-border="false"
          :pagination="pagination"
          :max-height="currentHeight"
          @page-change="handlePageChange"
          @page-limit-change="handlePageLimitChange">
          <bk-table-column label="No." prop="id" :width="80"></bk-table-column>
          <bk-table-column label="功能类型" prop="type" :width="80">
            <template slot-scope="props">
              <span>{{ props.row.is_builtin ? '系统' : '自定义' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column label="功能属性" prop="type_name" :width="80"></bk-table-column>
          <bk-table-column show-overflow-tooltip label="功能名称" prop="name"></bk-table-column>
          <bk-table-column show-overflow-tooltip label="功能描述" prop="desc">
            <template slot-scope="props">
              {{ props.row.desc || '--' }}
            </template>
          </bk-table-column>
          <bk-table-column show-overflow-tooltip label="关联数据表">
            <template slot-scope="props">
              <span>{{
                  props.row.relate_worksheet.length > 0
                    ? props.row.relate_worksheet.map(item => item.name).join(',')
                    : '--'
                }}</span>
            </template>
          </bk-table-column>
          <bk-table-column label="关联页面">
            <template slot-scope="props">
              <span>{{ props.row.relate_page.length ? props.row.relate_page.join(',') : '--' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column label="更新人">
            <template slot-scope="props">
              {{ props.row.updated_by || '--' }}
            </template>
          </bk-table-column>
          <bk-table-column label="更新时间" prop="update_at" :width="160"></bk-table-column>
          <bk-table-column label="状态" :width="160">
            <template slot-scope="props">
              <span class="bk-status-color"
                    :class="{ 'bk-status-primary': !props.row.is_valid }">
              </span>
              <span style="margin-left: 5px">
                    {{ props.row.is_valid ? '启用' : '未启用' }}
             </span>
            </template>
          </bk-table-column>
          <bk-table-column label="操作" :width="120" fixed="right">
            <template slot-scope="props">
              <bk-button
                :text="true"
                @click="onEditFunc(props.row)"
                :disabled="['IMPORT','EXPORT'].includes(props.row.type)">
                {{ props.row.is_builtin ? '查看' : '编辑' }}
              </bk-button>
              <bk-button
                v-if="!props.row.is_builtin"
                :text="true"
                @click="onDeleteFunc(props.row)"
                style="margin-left: 12px"
              >删除
              </bk-button
              >
            </template>
          </bk-table-column>
        </bk-table>
      </div>
    </page-wrapper>
  </section>
</template>
<script>
import PageWrapper from '@/components/pageWrapper.vue';
import searchItem from './searchItem.vue';
import { errorHandler } from '@/utils/errorHandler';
import searchTag from '../../application/components/searchTag.vue';
import Bus from '@/utils/bus.js';
import release from '../mixin/release';


export default {
  name: 'FunctionList',
  components: {
    PageWrapper,
    searchItem,
    searchTag,
  },
  mixins: [release],
  props: {
    appId: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      listData: [],
      listLoading: false,
      searchStr: '',
      pagination: {
        current: 1,
        count: 0,
        'limit-list': [15, 30, 50],
        limit: 15,
      },
      topStart: {
        content: '更多筛选条件',
        placement: 'top-start',
      },
      isShowSearchInfo: false,
      defaultTableHeight: '',
      showFiledMap: {
        funcType: '功能类型',
        attr: '功能属性',
        relate_worksheet: '关联表单',
        name: '功能名称',
      },
      searchForm: {},
    };
  },
  computed: {
    searchInfo() {
      const temparr = [];
      for (const key in this.searchForm) {
        if (this.searchForm[key] && this.showFiledMap[key]) {
          temparr.push({ name: this.showFiledMap[key], value: this.searchForm[key], key });
        }
      }
      return temparr;
    },
    currentHeight() {
      if (this.searchInfo.length > 0 && !this.isShowSearchInfo) {
        return this.defaultTableHeight - 38;
      }
      return this.defaultTableHeight;
    },
  },
  created() {
    this.defaultTableHeight = document.documentElement.clientHeight - 104 - 48 - 80 - 24;
    this.getFunctionList();
    this.loadConfigurInfo();
  },
  methods: {
    async getFunctionList(searParams) {
      try {
        this.listLoading = true;
        const params = {
          project_key: this.appId,
          page: this.pagination.current,
          page_size: this.pagination.limit,
          ...searParams,
        };
        const res = await this.$store.dispatch('setting/getFunctionList', params);
        this.pagination.count = res.data.count;
        this.listData = res.data.items;
      } catch (e) {
        console.error(e);
      } finally {
        this.listLoading = false;
      }
    },
    // 获取节点配置字段信息
    loadConfigurInfo() {
      return this.$store.dispatch('setting/getConfigurInfo').then((res) => {
        const value = res.data;
        const globalInfo = {};
        for (const key in value) {
          const listInfo = [];
          // 区分返回的是数组还是对象
          if (Array.isArray(value[key])) {
            for (let i = 0; i < value[key].length; i++) {
              if (Array.isArray(value[key][i])) {
                listInfo.push({
                  id: i + 1,
                  name: value[key][i][1] ? value[key][i][1] : '无',
                  typeName: value[key][i][0],
                });
              } else {
                listInfo.push(value[key][i]);
              }
            }
            globalInfo[key] = listInfo;
          } else {
            globalInfo[key] = value[key];
          }
        }
        /* 触发器隐藏部分触发事件
        * 节点触发器隐藏  分派单据 认领单据
        * 流程触发器隐藏  终止 挂起 恢复单据
        * 处理人隐藏 cmdb业务公用角色 通用角色表  权限中心角色
        * */
        globalInfo.processor_type.splice(0, 2);
        globalInfo.processor_type.splice(-1, 1);
        globalInfo.trigger_signals.STATE = { DELIVER_STATE: '转单', ENTER_STATE: '进入节点', LEAVE_STATE: '离开节点' };
        globalInfo.trigger_signals.FLOW = { CLOSE_TICKET: '关闭单据', CREATE_TICKET: '创建单据', DELETE_TICKET: '撤销单据' };
        this.$store.commit('setting/changeConfigur', globalInfo);
        sessionStorage.setItem('globalInfo', JSON.stringify(globalInfo));
      })
        .catch((res) => {
          errorHandler(res, this);
        });
    },
    handlePageChange(val) {
      this.pagination.current = val;
      this.getFunctionListAtPageChange();
    },
    handlePageLimitChange(val) {
      this.pagination.current = 1;
      this.pagination.limit = val;
      this.getFunctionListAtPageChange();
    },
    getFunctionListAtPageChange() {
      const { is_builtin, type, relate_worksheet, name } = this.searchForm;
      this.getFunctionList({
        is_builtin,
        type,
        worksheet_name__icontains: relate_worksheet,
        name__icontains: name,
      });
    },
    handleCreateFunction() {
      this.$router.push({ name: 'functionBasic', params: { appId: this.appId } });
    },
    onEditFunc(func) {
      this.$router.push({ name: 'functionBasic', params: { appId: this.appId, funcId: func.id } });
    },
    onDeleteFunc(func) {
      this.$bkInfo({
        type: 'warning',
        subTitle: `确认删除功能：${func.name}？`,
        confirmLoading: true,
        confirmFn: async () => {
          try {
            await this.$store.dispatch('setting/deleteFunction', func.id);
            if (this.listData.length === 1 && this.pagination.current > 1) {
              this.pagination.current -= 1;
            }
            this.getFunctionList();
          } catch (e) {
            console.error(e);
          } finally {
            this.appDeletePending = false;
          }
        },
      });
    },
    handleSearch(item) {
      this.searchForm = item;
      this.isShowSearchInfo = false;
      this.pagination.current = 1;
      const { is_builtin, type, relate_worksheet, name } = item;
      this.getFunctionList({
        is_builtin,
        type,
        worksheet_name__icontains: relate_worksheet,
        name__icontains: name,
      });
    },
    handleRemoveSearch(tag) {
      if (tag.key === 'attr') {
        this.searchForm.type = '';
      }
      if (tag.key === 'funcType') {
        this.searchForm.is_builtin = '';
      }
      this.searchForm[tag.key] = '';
      const { is_builtin, type, relate_worksheet, name } = this.searchForm;
      Bus.$emit('clearSearchItem', this.searchForm);
      this.getFunctionList({
        is_builtin,
        type,
        worksheet_name__icontains: relate_worksheet,
        name__icontains: name,
      });
    },
    handleCancel() {
      this.isShowSearchInfo = false;
      this.handleSearch();
    },
  },
};
</script>
<style lang="postcss" scoped>
@import '../../../css/scroller.css';
@import "../../../css/header-wrapper.css";

.page-main-wrapper {
  overflow: auto;
}

.list-table {
  margin: 24px;
  padding: 24px;
  background: #ffffff;
  box-shadow: 0 2px 4px 0 rgba(25, 25, 41, 0.05);
  border-radius: 2px;

  /deep/ .bk-table-body-wrapper {
    @mixin scroller;
  }

  /deep/ .bk-table {
    &::before {
      height: 0;
    }
  }
}

.search-icon {
  position: absolute;
  right: 0;
  top: 0;
  width: 32px;
  height: 32px;
  border: 1px solid #C4C6CC;
  cursor: pointer;
  border-radius: 2px;
  background: #FFFFFF;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;

  &:hover {
    border: 1px solid #979BA5;
  }

  i {
    color: #979BA5
  }
}

.search-info-container {
  margin-top: 8px;
  background: #F5F7FA;
}

.operate-area {
  position: relative;
  margin-bottom: 16px;
}

.search-item-container {
  display: flex;
  align-items: center;
  flex-wrap: wrap;

  /deep/ .bk-tag {
    margin: 4px 8px 2px 0;
  }
}

.bk-status-color {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #2DCB56;
}

.bk-status-primary {
  background-color: #3a84ff;
}
</style>
