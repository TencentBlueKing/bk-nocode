<template>
  <section>
    <page-wrapper title="管理员设置">
      <bk-tab :active.sync="active" style="margin-top: 20px;" ext-cls="setting-tab" :label-height="42"
      >
        <div class="tip-box" v-if="tipIsShow">
          <bk-icon type="info-circle" class="info" />
          应用管理员可以配置应用下所有表单、功能、页面、用户组权限并能管理所有应用数据
          <span class="add-member" @click="tipIsShow=false">
             不再提示
          </span>
        </div>
        <bk-tab-panel name="superAdmin" label="超级管理员">
          <super-admin @add="handleAddAdmin" ref="superAdmin"></super-admin>
        </bk-tab-panel>
        <bk-tab-panel name="applicationAdmin" label="应用管理员">
          <application-admin @addApp="handleAddAppAdmin" ref="applicationAdmin"></application-admin>
        </bk-tab-panel>
      </bk-tab>
    </page-wrapper>
    <bk-dialog
      ext-cls="my-custom"
      v-model="visible"
      theme="primary"
      width="640"
      :loading="dialogLoading"
      :mask-close="false"
      header-position="left"
      @confirm="handleSubmit"
      :title="title">
      <span class="second-title" v-if="dialogType==='applicationAdmin'">-用户管理</span>
      <bk-form :label-width="100" :model="formData">
        <bk-form-item label="添加成员" :property="'name'">
          <member-select v-model="formData.member"></member-select>
        </bk-form-item>
      </bk-form>
    </bk-dialog>
  </section>
</template>

<script>
import PageWrapper from '@/components/pageWrapper.vue';
import ApplicationAdmin from './component/applicationAdmin.vue';
import SuperAdmin from './component/superAdmin.vue';
import memberSelect from '../../components/memberSelect.vue';

export default {
  name: 'AdminSetting',
  components: {
    PageWrapper,
    ApplicationAdmin,
    SuperAdmin,
    memberSelect,
  },
  data() {
    return {
      active: 'superAdmin',
      tipIsShow: true,
      visible: false,
      dialogType: '',
      title: '',
      dialogLoading: false,
      formData: {
        member: [],
      },
    };
  },
  methods: {
    handleAddAdmin() {
      this.title = '添加超级管理员';
      this.dialogType = 'superAdmin';
      this.visible = true;
    },
    handleAddAppAdmin(row) {
      console.log(row);
      this.title = '添加应用管理员';
      this.dialogType = 'applicationAdmin';
      this.formData.member = row.owner;
      this.formData.project_key = row.key;
      this.visible = true;
    },
    async handleSubmit() {
      this.dialogLoading = true;
      if (this.dialogType === 'superAdmin') {
        this.addSuperAdmin();
      } else {
        this.addApplication();
      }
    },
    async addSuperAdmin() {
      const username = this.formData.member;
      const  params = {
        users: username,
        action: 'ADD',
      };
      try {
        const res = await this.$store.dispatch('manage/addSuperAdmin', params);
        if (res.result) {
          this.$bkMessage({
            message: '新增成功',
            theme: 'success',
          });
          this.formData.member = [];
          this.visible = false;
          await this.$refs.superAdmin.getFormsList(); await this.$refs.superAdmin.getFormsList();
        }
      } catch (e) {
        console.log(e);
      } finally {
        this.dialogLoading = false;
      }
    },
    async addApplication() {
      const username = this.formData.member;
      const  params = {
        users: username,
        action: 'ADD',
        project_key: this.formData.project_key,
      };
      try {
        const res = await this.$store.dispatch('manage/addApplicationAdmin', params);
        if (res.result) {
          this.$bkMessage({
            message: '新增成功',
            theme: 'success',
          });
          this.formData.member = [];
          this.formData.project_key = '';
          this.visible = false;
          await this.$refs.applicationAdmin.getAppList();
        }
      } catch (e) {
        console.log(e);
      } finally {
        this.dialogLoading = false;
      }
    },
  },
};
</script>
<style lang="postcss" scoped>

/deep/ .bk-table::before {
  height: 0;
}
/deep/ .bk-tab-section{
  background: #fff;
}
.setting-tab {
  background: #FFFFFF;
  margin: 24px;
}

.my-custom-dialog {
  position: relative;
}

.second-title {
  position: absolute;
  top: 22px;
  left: 171px;
  height: 22px;
  font-size: 14px;
  color: #979BA5;
}

.tip-box {
  position: relative;
  width: 100%;
  height: 32px;
  margin-bottom: 16px;
  border: 1px solid #C5DAFF;
  border-radius: 2px;
  background: #F0F8FF;
  font-size: 12px;
  color: #63656E;
  line-height: 32px;

  .info {
    margin: 0 8px 0 11px;
    color: #3A84FF;
    font-size: 14px !important;
    line-height: 32px;
  }

  .add-member {
    color: #3A84FF;
    position: absolute;
    right: 10px;
    cursor: pointer;
  }
}

.operate-area {
  position: relative;
  margin-bottom: 24px;
  height: 32px;

  .search-input {
    position: absolute;
    right: 0;
    top: 0;
    width: 240px;
  }
}
</style>
