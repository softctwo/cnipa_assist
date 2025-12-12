import React, { useMemo } from 'react';
import { Card, Descriptions, Button, Space, Typography, Alert, Tag } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';

const { Title, Paragraph } = Typography;

interface DocumentDetailData {
  id: number;
  title: string;
  applicant: string;
  status: 'pending' | 'examining' | 'completed' | 'rejected';
  filedDate: string;
  summary: string;
}

const statusMap: Record<DocumentDetailData['status'], { color: string; label: string }> = {
  pending: { color: 'orange', label: '待审查' },
  examining: { color: 'blue', label: '审查中' },
  completed: { color: 'green', label: '已完成' },
  rejected: { color: 'red', label: '已驳回' }
};

const DocumentDetail: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();

  const documentData = useMemo<DocumentDetailData>(() => ({
    id: Number(id) || 0,
    title: '一种新型节能门窗结构',
    applicant: '张三',
    status: 'pending',
    filedDate: '2024-03-08',
    summary:
      '本发明涉及一种具有双层密封结构的节能门窗系统，通过改进框体设计和隔热材料应用，提升建筑能效。'
  }), [id]);

  const { color, label } = statusMap[documentData.status];

  return (
    <div>
      <Space align="center" style={{ marginBottom: 16 }}>
        <Title level={2} style={{ margin: 0 }}>
          文档详情
        </Title>
        <Tag color={color}>{label}</Tag>
      </Space>
      <Paragraph type="secondary">
        查看专利文档的基本信息和摘要，可直接进入审查工作区继续处理。
      </Paragraph>

      <Alert
        message="提示"
        description="当前数据为示例内容，后续可与后端接口对接获取真实文档信息。"
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />

      <Card>
        <Descriptions bordered column={1} labelStyle={{ width: 160 }}>
          <Descriptions.Item label="申请号">CN{documentData.id.toString().padStart(6, '0')}</Descriptions.Item>
          <Descriptions.Item label="专利名称">{documentData.title}</Descriptions.Item>
          <Descriptions.Item label="申请人">{documentData.applicant}</Descriptions.Item>
          <Descriptions.Item label="提交日期">{documentData.filedDate}</Descriptions.Item>
          <Descriptions.Item label="摘要">{documentData.summary}</Descriptions.Item>
        </Descriptions>

        <Space style={{ marginTop: 24 }}>
          <Button onClick={() => navigate('/documents')}>返回列表</Button>
          <Button type="primary" onClick={() => navigate(`/examination/${documentData.id}`)}>
            进入审查工作区
          </Button>
        </Space>
      </Card>
    </div>
  );
};

export default DocumentDetail;
