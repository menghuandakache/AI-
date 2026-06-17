import ReactMarkdown from 'react-markdown'

export default function MarkdownViewer({ content }: { content: string }) {
  return (
    <div className="markdown-viewer">
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  )
}
