/**
 * API服务模块
 */
import axios, { AxiosResponse } from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 120000, // 2分钟超时
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data;
  },
  (error) => {
    console.error('API请求失败:', error);
    
    if (error.response) {
      // 服务器返回错误状态码
      const { status, data } = error.response;
      throw new Error(data.detail || `HTTP ${status} 错误`);
    } else if (error.request) {
      // 请求发送失败
      throw new Error('网络连接失败，请检查后端服务是否启动');
    } else {
      // 其他错误
      throw new Error(error.message || '未知错误');
    }
  }
);

// API接口定义
export const apiService = {
  // 文档相关API
  uploadDocument: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  getDocuments: (skip: number = 0, limit: number = 20) => {
    return api.get(`/documents/list?skip=${skip}&limit=${limit}`);
  },

  getDocumentDetail: (id: number) => {
    return api.get(`/documents/${id}`);
  },

  deleteDocument: (id: number) => {
    return api.delete(`/documents/${id}`);
  },

  // 审查相关API
  startExamination: (applicationId: number, examinationType: string = 'formal', ruleTypes?: string[]) => {
    return api.post('/examination/start', {
      application_id: applicationId,
      examination_type: examinationType,
      rule_types: ruleTypes,
    });
  },

  getExaminationHistory: (applicationId: number) => {
    return api.get(`/examination/history/${applicationId}`);
  },

  getExaminationRules: () => {
    return api.get('/examination/rules');
  },

  // AI相关API
  getAIStatus: () => {
    return api.get('/ai/status');
  },

  analyzeWithAI: (applicationId: number, examinationType: string = 'comprehensive') => {
    return api.post('/examination/ai-analysis', {
      application_id: applicationId,
      examination_type: examinationType,
    });
  },

  analyzeText: (text: string, analysisType: string = 'comprehensive') => {
    return api.post('/ai/analyze', {
      text,
      analysis_type: analysisType,
    });
  },

  generateOpinion: (analysisResult: string, opinionType: string = 'notice') => {
    return api.post('/ai/generate-opinion', {
      analysis_result: analysisResult,
      opinion_type: opinionType,
    });
  },

  testAIConnection: () => {
    return api.post('/ai/test-connection');
  },
};

// 类型定义
export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data: T;
  error_message?: string;
}

export interface PatentDocument {
  id: number;
  application_number: string;
  application_date: string;
  title: string;
  applicant: string;
  inventor?: string;
  status: string;
  created_at: string;
}

export interface PatentContent {
  technical_field?: string;
  background_art?: string;
  invention_content?: string;
  claims?: string[];
  description?: string;
  abstract?: string;
}

export interface ExaminationResult {
  rule_name: string;
  rule_type: string;
  result: 'pass' | 'fail' | 'warning' | 'skip';
  confidence: number;
  message: string;
  execution_time: number;
}

export interface AIAnalysisResult {
  content: string;
  confidence: number;
  processing_time: number;
  model_used: string;
}

export default api;