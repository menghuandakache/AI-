import { Form, Input, Select } from 'antd'

interface Props {
  form: any
  initialValues?: Record<string, any>
}

export default function KnowledgeBaseForm({ form, initialValues }: Props) {
  return (
    <Form form={form} layout="vertical" initialValues={initialValues}>
      <Form.Item name="name" label="知识库名称" rules={[{ required: true }]}>
        <Input placeholder="请输入知识库名称" maxLength={200} />
      </Form.Item>
      <Form.Item name="description" label="描述">
        <Input.TextArea rows={3} placeholder="请输入知识库描述" />
      </Form.Item>
      <Form.Item name="domain" label="业务域">
        <Select placeholder="选择业务域" options={[
          { value: 'Finance', label: '财务' },
          { value: 'HR', label: '人事' },
          { value: 'Legal', label: '法务' },
          { value: 'Procurement', label: '采购' },
          { value: 'Workplace', label: '职场' },
        ]} />
      </Form.Item>
    </Form>
  )
}
