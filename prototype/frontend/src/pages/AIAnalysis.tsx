import React, { useState } from 'react';
import { Card, Typography, Input, Button, List, Space, Tag, Alert } from 'antd';
import { RobotOutlined, LoadingOutlined } from '@ant-design/icons';

const { Title, Paragraph, Text } = Typography;
const { TextArea } = Input;

interface AnalysisResult {
  title: string;
  content: string;
  tag?: string;
}

const AIAnalysis: React.FC = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<AnalysisResult[]>([]);

  const handleAnalyze = () => {
    setLoading(true);
    setTimeout(() => {
      setResults([
        {
          title: '权利要求撰写建议',
          content: '建议突出节能结构的核心创新点，明确框体材料和密封方案的技术效果。',
          tag: '建议'
        },
        {
          title: '新颖性风险',
          content: '检索到相似的窗框结构专利，请在实质审查阶段重点验证差异点。',
          tag: '风险'
        }
      ]);
      setLoading(false);
    }, 800);
  };

  return (
    <div>
      <Title level={2}>AI智能分析</Title>
      <Paragraph type="secondary">
        输入需求或审查问题，调用本地AI服务获取初步分析和建议，辅助审查决策。
      </Paragraph>

      <Card style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Text>分析问题或提示</Text>
          <TextArea
            rows={4}
            placeholder="例如：请给出权利要求1的新颖性分析要点..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <Button type="primary" icon={loading ? <LoadingOutlined /> : <RobotOutlined />} onClick={handleAnalyze}>
            生成分析
          </Button>
        </Space>
      </Card>

      <Card title="分析结果">
        {!results.length && !loading && (
          <Alert message="尚无分析结果" description="提交问题后将在此展示AI返回的内容。" type="info" showIcon />
        )}
        <List
          itemLayout="vertical"
          dataSource={results}
          renderItem={(item) => (
            <List.Item
              key={item.title}
              extra={item.tag ? <Tag color="blue">{item.tag}</Tag> : null}
            >
              <List.Item.Meta
                title={item.title}
                description={<Text type="secondary">AI生成的内容，请人工核查后使用。</Text>}
              />
              {item.content}
            </List.Item>
          )}
        />
      </Card>
    </div>
  );
};

export default AIAnalysis;
