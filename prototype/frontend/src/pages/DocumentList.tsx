import React, { useMemo } from 'react';
import { Table, Tag, Button, Space, Typography, Card } from 'antd';
import { useNavigate } from 'react-router-dom';

const { Title, Paragraph, Text } = Typography;

interface DocumentRecord {
  id: number;
  title: string;
  applicant: string;
  status: 'pending' | 'examining' | 'completed' | 'rejected';
  filedDate: string;
}

const statusMap: Record<DocumentRecord['status'], { color: string; label: string }> = {
  pending: { color: 'orange', label: '待审查' },
  examining: { color: 'blue', label: '审查中' },
  completed: { color: 'green', label: '已完成' },
  rejected: { color: 'red', label: '已驳回' }
};

const DocumentList: React.FC = () => {
  const navigate = useNavigate();

  const dataSource = useMemo<DocumentRecord[]>(
    () => [
      {
        id: 1,
        title: '一种新型节能门窗结构',
        applicant: '张三',
        status: 'pending',
        filedDate: '2024-03-08'
      },
      {
        id: 2,
        title: '智能巡检无人机控制系统',
        applicant: '李四',
        status: 'examining',
        filedDate: '2024-02-21'
      },
      {
        id: 3,
        title: '基于物联网的环境监测设备',
        applicant: '王五',
        status: 'completed',
        filedDate: '2024-01-15'
      },
      {
        id: 4,
        title: '可调节式防滑地砖',
        applicant: '赵六',
        status: 'rejected',
        filedDate: '2023-12-30'
      }
    ],
    []
  );

  const columns = [
    {
      title: '申请号',
      dataIndex: 'id',
      key: 'id',
      width: 100,
      render: (value: number) => <Text strong>CN{value.toString().padStart(6, '0')}</Text>
    },
    {
      title: '专利名称',
      dataIndex: 'title',
      key: 'title'
    },
    {
      title: '申请人',
      dataIndex: 'applicant',
      key: 'applicant',
      width: 160
    },
    {
      title: '提交日期',
      dataIndex: 'filedDate',
      key: 'filedDate',
      width: 140
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: DocumentRecord['status']) => {
        const { color, label } = statusMap[status];
        return <Tag color={color}>{label}</Tag>;
      }
    },
    {
      title: '操作',
      key: 'actions',
      width: 220,
      render: (_: unknown, record: DocumentRecord) => (
        <Space>
          <Button type="link" onClick={() => navigate(`/documents/${record.id}`)}>
            查看详情
          </Button>
          <Button type="primary" onClick={() => navigate(`/examination/${record.id}`)}>
            开始审查
          </Button>
        </Space>
      )
    }
  ];

  return (
    <div>
      <Title level={2}>专利文档</Title>
      <Paragraph type="secondary">
        在此查看和管理所有已上传的专利文档，支持快速跳转到审查工作区。
      </Paragraph>

      <Card>
        <Table
          rowKey="id"
          dataSource={dataSource}
          columns={columns}
          pagination={{ pageSize: 5 }}
        />
      </Card>
    </div>
  );
};

export default DocumentList;
