import React, { useMemo } from 'react';
import { Card, Steps, Typography, Space, Button, Alert, Row, Col, Timeline, Tag } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';

const { Title, Paragraph, Text } = Typography;

const ExaminationWorkspace: React.FC = () => {
  const { id } = useParams<{ id?: string }>();
  const navigate = useNavigate();

  const documentTitle = useMemo(() => (
    id ? `申请号 CN${id.toString().padStart(6, '0')}` : '未选择具体文档'
  ), [id]);

  const timelineItems = [
    { color: 'green', children: '完成形式审查' },
    { color: 'blue', children: 'AI初步分析完成，等待人工确认' },
    { color: 'gray', children: '准备撰写审查意见通知书' }
  ];

  return (
    <div>
      <Title level={2}>审查工作区</Title>
      <Paragraph type="secondary">
        在此集中处理审查任务，包括阅读文档、记录发现以及生成审查意见。
      </Paragraph>

      {!id && (
        <Alert
          message="未选择文档"
          description="通过仪表板或文档列表选择一份专利文档后进入该页面，可在此继续审查流程。"
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      <Space align="center" style={{ marginBottom: 24 }}>
        <Text strong>当前文档：</Text>
        <Tag color="geekblue">{documentTitle}</Tag>
        <Button type="link" onClick={() => navigate('/documents')}>
          选择其他文档
        </Button>
      </Space>

      <Row gutter={[16, 16]}>
        <Col xs={24} md={14}>
          <Card title="审查进度">
            <Steps
              current={1}
              items={[
                { title: '形式审查' },
                { title: '实质审查' },
                { title: '生成意见' },
                { title: '完成' }
              ]}
            />
            <Paragraph style={{ marginTop: 16 }}>
              使用左侧进度跟踪审查阶段，完成后可生成审查报告或继续补充说明。
            </Paragraph>
            <Space>
              <Button type="primary">保存进度</Button>
              <Button onClick={() => navigate('/ai-analysis')}>AI辅助分析</Button>
            </Space>
          </Card>
        </Col>

        <Col xs={24} md={10}>
          <Card title="工作日志">
            <Timeline items={timelineItems} />
            <Paragraph type="secondary" style={{ marginTop: 16 }}>
              记录审查过程中的关键节点，便于后续追踪和复盘。
            </Paragraph>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default ExaminationWorkspace;
