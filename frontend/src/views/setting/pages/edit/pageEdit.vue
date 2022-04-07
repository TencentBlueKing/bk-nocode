<template>
  <div class="page-edit">
    <bk-form
      form-type="vertical"
      :model="pageData"
      :rules="rules">
      <bk-form-item
        v-if="type==='LINK_GROUP'"
        label="组名称"
        error-display-type="normal"
        property="name"
        :required="true">
        <bk-input v-model.trim="pageData.name">
        </bk-input>
      </bk-form-item>
      <bk-form-item
        v-if="type==='LINK_GROUP'"
        label="按钮分布">
        <bk-select v-model="pageData.layout.display">
          <bk-option v-for="item in displayList" :key="item.id" :id="item.id" :name="item.name"></bk-option>
        </bk-select>
      </bk-form-item>
      <bk-form-item
        v-if="type==='FUNCTION_GROUP'"
        label="入口名称">
        <bk-input v-model.trim="pageData.config.name" @change="change">
        </bk-input>
      </bk-form-item>
      <bk-form-item
        v-if="type==='FUNCTION_GROUP'"
        label="功能绑定">
        <bk-select
          v-model="pageData.value"
          :clearable="false"
          :loading="functionListLoading"
          @selected="change">
          <bk-option
            v-for="func in functionList"
            :key="func.id"
            :id="func.id"
            :name="func.name">
          </bk-option>
        </bk-select>
      </bk-form-item>
      <bk-form-item
        v-if="type==='FUNCTION_GROUP'"
        label="logo">
        <div class="upload">
          选择文件
          <input
            class="upload-btn"
            type="file"
            accept="image/png,image/jpg,image/JPEG"
            @change="changeImg($event)"
            ref="referenceUpload"
          >
          <span class="upload-desc">支持扩展名：.jpg,.png,.JPEG</span>
        </div>
      </bk-form-item>
      <bk-form-item
        v-if="type==='FUNCTION_GROUP'"
        label="入口描述">
        <bk-input
          placeholder="请输入描述信息"
          :type="'textarea'"
          :rows="3"
          :maxlength="255"
          v-model="pageData.config.desc"
          @change="change">
        </bk-input>
      </bk-form-item>
      <bk-form-item
        label="布局">
        <bk-radio-group v-model="pageData.layout.lineLayout" @change="change">
          <bk-radio :value="'COL_3'">
            1/4行
          </bk-radio>
          <bk-radio :value="'COL_6'">
            半行
          </bk-radio>
          <bk-radio :value="'COL_9'">
            3/4行
          </bk-radio>
          <bk-radio :value="'COL_12'">
            整行
          </bk-radio>
        </bk-radio-group>
      </bk-form-item>
    </bk-form>
  </div>
</template>

<script>
import cloneDeep from 'lodash.clonedeep';

export default {
  name: 'PageEdit',
  props: {
    page: {
      type: Object,
      default: () => ({}),
    },
    type: [String],
  },
  data() {
    return {
      pageData: cloneDeep(this.page),
      functionListLoading: false,
      functionList: [],
      displayList: [{
        id: 'row',
        name: '横向分布',
      },
      {
        id: 'column',
        name: '横向分布',
      }],
      rules: {
        name: [
          {
            required: true,
            trigger: 'blur',
            message: '组名称为必填项',
          },
        ],
      },
    };
  },
  watch: {
    page(val) {
      this.pageData = cloneDeep(this.page);
    },
  },
  created() {
    this.getFunctionList();
  },
  methods: {
    async getFunctionList() {
      try {
        this.functionListLoading = true;
        const params = {
          project_key: this.$route.params?.appId,
        };
        const res = await this.$store.dispatch('setting/getFunctionBindList', params);
        this.functionList = res.data.filter(item => !item.is_builtin && ['ADD'].includes(item.type));
      } catch (e) {
        console.error(e);
      } finally {
        this.functionListLoading = false;
      }
    },
    changeImg(e) {
      const _this = this;
      const  file = e.target.files;
      const reader = new FileReader();
      reader.readAsDataURL(file[0]);
      reader.onload = function (e) {
        // 读取到的图片 base64 数据编码 将此编码字符串传给后台即可
        let imgBase64Code = e.target.result;
        // 截取头部信息。统一 jpeg 显示
        imgBase64Code = imgBase64Code.replace(/^data:image\/\w+;base64,/, '');
        _this.pageData.config.path = imgBase64Code;
        _this.change();
      };
    },
    change() {
      this.$emit('change', this.pageData);
    },
  },
};
</script>

<style scoped lang="postcss">
/deep/ .bk-form-radio {
  font-size: 12px;

  &:last-child {
    margin-right: 0
  }
}

.upload{
  width: 88px;
  height: 32px;
  background: #FFFFFF;
  border: 1px solid #C4C6CC;
  border-radius: 2px;
  position: relative;
  font-size: 14px;
  color: #63656E;
  text-align: center;
  &:hover{
    cursor: pointer;
  }
}

.upload-btn {
  width: 88px;
  opacity: 0;
  position: absolute;
  right: 0;
  top: 0;
  z-index: 10;
  &:hover{
    cursor: pointer;
  }
}
.upload-desc{
  font-size: 12px;
  color: #63656E;
  position: absolute;
  left: 22px;
  width: 300px;
  display: inline-block;
}
</style>
