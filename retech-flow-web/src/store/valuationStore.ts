/**
 * 智能估价页专用状态管理
 *
 * 通过 createValuationStore 工厂创建。
 */
import { createValuationStore } from './createValuationStore'

export type { ValuationResult } from './createValuationStore'

export const useValuationStore = createValuationStore(
  'valuation',
  'Valuation'
)
