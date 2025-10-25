/**
 * 文档管理状态切片
 */
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { apiService, PatentDocument, PatentContent } from '../services/api';

// 异步操作
export const fetchDocuments = createAsyncThunk(
  'documents/fetchDocuments',
  async ({ skip = 0, limit = 20 }: { skip?: number; limit?: number } = {}) => {
    const response = await apiService.getDocuments(skip, limit);
    return response.data;
  }
);

export const fetchDocumentDetail = createAsyncThunk(
  'documents/fetchDocumentDetail',
  async (id: number) => {
    const response = await apiService.getDocumentDetail(id);
    return response.data;
  }
);

export const uploadDocument = createAsyncThunk(
  'documents/uploadDocument',
  async (file: File) => {
    const response = await apiService.uploadDocument(file);
    return response.data;
  }
);

export const deleteDocument = createAsyncThunk(
  'documents/deleteDocument',
  async (id: number) => {
    await apiService.deleteDocument(id);
    return id;
  }
);

// 状态接口
interface DocumentsState {
  documents: PatentDocument[];
  currentDocument: PatentDocument | null;
  currentDocumentContent: PatentContent | null;
  total: number;
  loading: boolean;
  error: string | null;
  uploadProgress: number;
}

// 初始状态
const initialState: DocumentsState = {
  documents: [],
  currentDocument: null,
  currentDocumentContent: null,
  total: 0,
  loading: false,
  error: null,
  uploadProgress: 0,
};

// 创建切片
const documentsSlice = createSlice({
  name: 'documents',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setUploadProgress: (state, action: PayloadAction<number>) => {
      state.uploadProgress = action.payload;
    },
    clearCurrentDocument: (state) => {
      state.currentDocument = null;
      state.currentDocumentContent = null;
    },
  },
  extraReducers: (builder) => {
    // 获取文档列表
    builder
      .addCase(fetchDocuments.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDocuments.fulfilled, (state, action) => {
        state.loading = false;
        state.documents = action.payload.applications || [];
        state.total = action.payload.total || 0;
      })
      .addCase(fetchDocuments.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '获取文档列表失败';
      });

    // 获取文档详情
    builder
      .addCase(fetchDocumentDetail.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDocumentDetail.fulfilled, (state, action) => {
        state.loading = false;
        state.currentDocument = action.payload.application_info;
        state.currentDocumentContent = action.payload.patent_content;
      })
      .addCase(fetchDocumentDetail.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '获取文档详情失败';
      });

    // 上传文档
    builder
      .addCase(uploadDocument.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.uploadProgress = 0;
      })
      .addCase(uploadDocument.fulfilled, (state, action) => {
        state.loading = false;
        state.uploadProgress = 100;
        // 可以选择将新文档添加到列表中
        // state.documents.unshift(action.payload.patent_info);
      })
      .addCase(uploadDocument.rejected, (state, action) => {
        state.loading = false;
        state.uploadProgress = 0;
        state.error = action.error.message || '文档上传失败';
      });

    // 删除文档
    builder
      .addCase(deleteDocument.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteDocument.fulfilled, (state, action) => {
        state.loading = false;
        state.documents = state.documents.filter(doc => doc.id !== action.payload);
        state.total = Math.max(0, state.total - 1);
      })
      .addCase(deleteDocument.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '删除文档失败';
      });
  },
});

export const { clearError, setUploadProgress, clearCurrentDocument } = documentsSlice.actions;
export default documentsSlice.reducer;