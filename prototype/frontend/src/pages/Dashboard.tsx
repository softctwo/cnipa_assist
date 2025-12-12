import React, { useEffect, useState } from 'react';
import { 
  Row, 
  Col, 
  Card, 
  Statistic, 
  Button, 
  List, 
  Typography, 
  Space,
  Alert,
  Progress,
  Tag
} from 'antd';
import {
  FileTextOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  PlusOutlined,
  RobotOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';

const { Title, Text } = Typography;

interface DashboardStats {
  totalDocuments: number;
  pendingExaminations: number;
  completedExaminations: number;
  aiAnalysisCount: number;
}

interface RecentDocument {
  id: number;
  title: string;
  applicant: string;
  status: string;
  created_at: string;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats>({
    totalDocuments: 0,
    pendingExaminations: 0,
    completedExaminations: 0,
    aiAnalysisCount: 0
  });
  const [recentDocuments, setRecentDocuments] = useState<RecentDocument[]>([]);
  const [aiStatus, setAiStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // 加载文档列表
      const documentsResponse = await apiService.getDocuments();
      const documents = documentsResponse.data.applications || [];
      
      // 加载AI状态
      const aiStatusResponse = await apiService.getAIStatus();
      setAiStatus(aiStatusResponse.data);
      
      // 计算统计数据
      const totalDocuments = documents.length;
      const pendingExaminations = documents.filter((doc: any) => doc.status === 'pending').length;
      const completedExaminations = documents.filter((doc: any) => doc.status === 'completed').length;
      
      setStats({
        totalDocuments,
        pendingExaminations,
        completedExaminations,
        aiAnalysisCount: 0 // 暂时设为0，后续从审查记录中统计
      });
      
      // 设置最近文档（取前5个）
      setRecentDocuments(documents.slice(0, 5));
      
    } catch (error) {
      console.error('加载仪表板数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadDocument = () => {
    navigate('/documents');
  };

  const handleStartExamination = (documentId: number) => {
    navigate(`/examination/${documentId}`);
  };

  const getStatusTag = (status: string) => {
    const statusMap: { [key: string]: { color: string; text: string } } = {
      'pending': { color: 'orange', text: '待审查' },
      'examining': { color: 'blue', text: '审查中' },
      'completed': { color: 'green', text: '已完成' },
      'rejected': { color: 'red', text: '已驳回' }
    };
    
    const statusInfo = statusMap[status] || { color: 'default', text: status };
    return <Tag color={statusInfo.color}>{statusInfo.text}</Tag>;
  };

  const getAIStatusAlert = () => {
    if (!aiStatus) return null;
    
    const { service_status, model_availability } = aiStatus;
    
    if (service_status === 'available' && model_availability.primary_model) {
      return (
        <Alert
          message="AI服务正常"
          description="本地AI模型运行正常，可以使用智能审查功能"
          type="success"
          showIcon
          icon={<RobotOutlined />}
        />
      );
    } else if (service_status === 'available' && !model_availability.primary_model) {
      return (
        <Alert
          message="AI模型未就绪"
          description="Ollama服务运行正常，但主要模型未下载。请在设置中下载模型。"
          type="warning"
          showIcon
          action={
            <Button size="small" onClick={() => navigate('/settings')}>
              去设置
            </Button>
          }
        />
      );
    } else {
      return (
        <Alert
          message="AI服务不可用"
          description="无法连接到本地AI服务，请检查Ollama是否正在运行"
          type="error"
          showIcon
          action={
            <Button size="small" onClick={() => navigate('/settings')}>
              查看详情
            </Button>
          }
        />
      );
    }
  };

  return (
    <div>
      <Row gutter={[24, 24]}>
        {/* 页面标题和快捷操作 */}
        <Col span={24}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Title level={2}>工作台</Title>
            <Space>
              <Button 
                type="primary" 
                icon={<PlusOutlined />}
                onClick={handleUploadDocument}
              >
                上传专利文档
              </Button>
              <Button onClick={() => navigate('/ai-analysis')}>
                AI智能分析
              </Button>
            </Space>
          </div>
        </Col>

        {/* AI状态提醒 */}
        <Col span={24}>
          {getAIStatusAlert()}
        </Col>

        {/* 统计卡片 */}
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="专利文档总数"
              value={stats.totalDocuments}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="待审查"
              value={stats.pendingExaminations}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="已完成"
              value={stats.completedExaminations}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="AI分析次数"
              value={stats.aiAnalysisCount}
              prefix={<RobotOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>

        {/* 最近文档 */}
        <Col xs={24} lg={16}>
          <Card 
            title="最近文档" 
            extra={<Button type="link" onClick={() => navigate('/documents')}>查看全部</Button>}
          >
            <List
              loading={loading}
              dataSource={recentDocuments}
              renderItem={(item) => (
                <List.Item
                  actions={[
                    <Button 
                      type="link" 
                      onClick={() => navigate(`/documents/${item.id}`)}
                    >
                      查看
                    </Button>,
                    <Button 
                      type="link" 
                      onClick={() => handleStartExamination(item.id)}
                    >
                      审查
                    </Button>
                  ]}
                >
                  <List.Item.Meta
                    title={
                      <Space>
                        <Text strong>{item.title || '未识别标题'}</Text>
                        {getStatusTag(item.status)}
                      </Space>
                    }
                    description={
                      <Space direction="vertical" size={4}>
                        <Text type="secondary">申请人: {item.applicant || '未识别'}</Text>
                        <Text type="secondary">
                          上传时间: {item.created_at ? new Date(item.created_at).toLocaleString() : '未知'}
                        </Text>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>

        {/* 系统状态 */}
        <Col xs={24} lg={8}>
          <Card title="系统状态">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text>文档解析引擎</Text>
                <Progress percent={100} size="small" status="success" />
              </div>
              
              <div>
                <Text>规则引擎</Text>
                <Progress percent={100} size="small" status="success" />
              </div>
              
              <div>
                <Text>AI服务</Text>
                <Progress 
                  percent={aiStatus?.service_status === 'available' ? 100 : 0} 
                  size="small" 
                  status={aiStatus?.service_status === 'available' ? 'success' : 'exception'}
                />
              </div>
              
              <div>
                <Text>数据库</Text>
                <Progress percent={100} size="small" status="success" />
              </div>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;