// frontend/src/lib/markdown.ts
// Markdown 渲染工具：使用 marked + DOMPurify 确保安全渲染

import DOMPurify from 'dompurify'
import { marked } from 'marked'

// 配置 marked：启用 GFM（GitHub Flavored Markdown）
marked.setOptions({
  gfm: true,
  breaks: true,
})

/**
 * 将 Markdown 文本转为安全的 HTML
 * 使用 DOMPurify 过滤 XSS 风险标签
 */
export function renderMarkdown(text: string): string {
  if (!text) return ''
  const rawHtml = marked.parse(text) as string
  return DOMPurify.sanitize(rawHtml, {
    ALLOWED_TAGS: [
      'p', 'br', 'strong', 'em', 'code', 'pre', 'blockquote',
      'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'a', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'hr',
      'span', 'div',
    ],
    ALLOWED_ATTR: ['href', 'target', 'rel', 'class'],
  })
}

/**
 * 判断文本是否包含 Markdown 语法
 * 用于决定是否需要渲染为 HTML
 */
export function hasMarkdownSyntax(text: string): boolean {
  return /^#{1,6}\s|^\* |^- |^\d+\. |```|\*\*|__|`[^`]+`|\[.+\]\(.+\)/m.test(text)
}
