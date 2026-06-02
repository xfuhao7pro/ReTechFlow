/**
 * 发布页智能估价专用状态管理
 *
 * 通过 createValuationStore 工厂创建。
 */
import { createValuationStore } from './createValuationStore'

export type { ValuationResult } from './createValuationStore'

export const usePublishValuationStore = createValuationStore(
  'publishValuation',
  'Publish'
)
