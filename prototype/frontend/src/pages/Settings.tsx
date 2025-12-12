import React, { useState } from 'react';
import { Card, Typography, Switch, Divider, Space, Button, Form, InputNumber, Alert } from 'antd';

const { Title, Paragraph, Text } = Typography;

const Settings: React.FC = () => {
  const [aiEnabled, setAiEnabled] = useState(true);
  const [autoSave, setAutoSave] = useState(true);

  return (
    <div>
      <Title level={2}>系统设置</Title>
      <Paragraph type="secondary">
        配置审查助手的常用选项，包括AI服务、自动保存以及性能参数。
      </Paragraph>

      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <Card title="AI服务">
          <Space align="center" size="large">
            <Text>启用本地AI能力</Text>
            <Switch checked={aiEnabled} onChange={setAiEnabled} />
            <Text type="secondary">关闭后将仅提供手动审查功能</Text>
          </Space>
        </Card>

        <Card title="编辑偏好">
          <Space align="center" size="large">
            <Text>自动保存审查记录</Text>
            <Switch checked={autoSave} onChange={setAutoSave} />
          </Space>
          <Divider />
          <Form layout="inline">
            <Form.Item label="自动保存间隔(秒)">
              <InputNumber min={10} max={600} defaultValue={60} />
            </Form.Item>
            <Button type="primary">保存设置</Button>
          </Form>
        </Card>

        <Card title="系统提示">
          <Alert
            message="注意"
            description="当前为示例设置页面，后续可与后端接口对接以持久化用户配置。"
            type="info"
            showIcon
          />
        </Card>
      </Space>
    </div>
  );
};

export default Settings;
