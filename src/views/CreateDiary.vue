<template>
  <div class="diary-container">
    <h1>发布旅游日记</h1>
    <el-form ref="formRef" :model="form" label-width="80px" :rules="rules">
      <!-- 标题 -->
      <el-form-item label="标题" prop="title">
        <el-input v-model="form.title" placeholder="请输入日记标题" />
      </el-form-item>

      <!-- 旅行日期 -->
      <el-form-item label="旅行日期" prop="date">
        <el-date-picker
          v-model="form.date"
          type="date"
          placeholder="选择日期"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>

      <!-- 地点选择 -->
      <el-form-item label="地点" prop="spot_id">
        <el-select
          v-model="form.spot_id"
          placeholder="请选择旅行地点"
          filterable
        >
          <el-option
            v-for="item in locations"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>

      <!-- 图片上传 -->
      <el-form-item label="照片">
        <el-upload
          action="#"
          list-type="picture-card"
          :auto-upload="false"
          :on-change="handleUpload"
          :on-preview="handlePreview"
          :on-remove="handleRemove"
          :file-list="fileList"
          multiple
        >
          <el-icon><Plus /></el-icon>
        </el-upload>
      </el-form-item>

      <!-- 添加图片预览对话框 -->
      <el-dialog v-model="dialogVisible">
        <img w-full :src="dialogImageUrl" alt="Preview Image" />
      </el-dialog>
      <!-- 日记内容 -->
      <el-form-item label="内容" prop="content">
        <el-input
          v-model="form.content"
          type="textarea"
          :rows="6"
          placeholder="记录你的旅行故事..."
        />
      </el-form-item>

      <!-- 提交按钮 -->
      <el-form-item>
        <el-button type="primary" @click="submitForm">立即发布</el-button>
        <el-button @click="resetForm">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { Plus } from "@element-plus/icons-vue";
import { useRouter } from "vue-router";
import { createJournal, getAttractionsList } from "@/api/journals";

const router = useRouter();
const user = JSON.parse(localStorage.getItem('user'));
const formRef = ref(null);  // 添加表单引用
const fileList = ref([]);   // 添加文件列表定义

// 表单数据
const form = reactive({
  title: "",
  date: "",
  spot_id: null,  // 统一使用spot_id
  content: "",
});

// 地点选项
const locations = ref([]);

// 获取景点列表
onMounted(async () => {
  try {
    const res = await getAttractionsList();
    locations.value = res.data.data.map(item => ({
      value: item[0],  // spot_id
      label: item[1]   // spot_name
    }));
  } catch (error) {
    ElMessage.error('获取景点列表失败');
  }
});

// 表单验证规则
const rules = reactive({
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' },
    { min: 3, max: 30, message: '长度在3到30个字符', trigger: 'blur' }
  ],
  date: [
    { required: true, message: '请选择日期', trigger: 'change' }
  ],
  spot_id: [
    { required: true, message: '请选择地点', trigger: 'change' }
  ],
  content: [
    { required: true, message: '请输入内容', trigger: 'blur' },
    { min: 10, message: '内容至少10个字符', trigger: 'blur' }
  ]
});

// 提交表单
const submitForm = async () => {
  try {
    // 先验证表单
    await formRef.value.validate();
    
    const formData = new FormData();
    formData.append("title", form.title);
    formData.append("date", form.date);
    formData.append("spot_id", form.spot_id);
    formData.append("content", form.content);
    formData.append("user_id", user.id);

    fileList.value.forEach((file) => {
      formData.append("imgs", file.raw);
    });

    await createJournal(formData);
    ElMessage.success("日记发布成功！");
    router.push('/all-diaries');
  } catch (error) {
    if (error.name !== 'ValidationError') {
      ElMessage.error("日记发布失败");
    }
  }
};

// 图片上传处理函数
const handleUpload = (file) => {
  fileList.value.push(file);
};

// 重置表单
const resetForm = () => {
  formRef.value.resetFields();
  fileList.value = [];
};

// 在script setup部分添加以下代码
const dialogVisible = ref(false);
const dialogImageUrl = ref('');

// 图片预览处理
const handlePreview = (file) => {
  dialogImageUrl.value = file.url || URL.createObjectURL(file.raw);
  dialogVisible.value = true;
};

// 图片删除处理
const handleRemove = (file) => {
  const index = fileList.value.findIndex(f => f.uid === file.uid);
  if (index !== -1) {
    fileList.value.splice(index, 1);
  }
};
</script>

<style scoped>
.diary-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

h1 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 30px;
}

.el-select {
  width: 100%;
}

.el-textarea__inner {
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", sans-serif;
}
</style>