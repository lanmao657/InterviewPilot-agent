// frontend/src/stores/toast.ts
// 全局 Toast 通知状态管理

import { defineStore } from 'pinia'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface Toast {
  id: string
  type: ToastType
  message: string
  duration: number
}

interface ToastState {
  toasts: Toast[]
}

function newId(): string {
  return `toast-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

export const useToastStore = defineStore('toast', {
  state: (): ToastState => ({ toasts: [] }),
  actions: {
    /** 显示一条 Toast 消息 */
    show(message: string, type: ToastType = 'info', duration = 3000) {
      const toast: Toast = { id: newId(), type, message, duration }
      this.toasts.push(toast)
      if (duration > 0) {
        setTimeout(() => this.dismiss(toast.id), duration)
      }
    },
    /** 快捷方法 */
    success(message: string) { this.show(message, 'success') },
    error(message: string) { this.show(message, 'error', 5000) },
    warning(message: string) { this.show(message, 'warning', 4000) },
    info(message: string) { this.show(message, 'info') },
    /** 关闭指定 Toast */
    dismiss(id: string) {
      const idx = this.toasts.findIndex((t) => t.id === id)
      if (idx !== -1) this.toasts.splice(idx, 1)
    },
    /** 清空所有 */
    clear() { this.toasts = [] },
  },
})
