import { ref, type Ref } from 'vue'

/**
 * 打字机效果 composable
 * 可复用于智能估价页和发布商品页，向指定 Ref 逐字写入文本
 */
export function useTypewriter(speed = 50) {
  const isTypingTitle = ref(false)
  const isTypingDesc = ref(false)
  let cancelled = false

  /** 向目标 ref 逐字写入文本 */
  async function typeText(
    text: string,
    target: Ref<string>,
    isTypingFlag: Ref<boolean>
  ) {
    isTypingFlag.value = true
    target.value = ''

    const chars = text.split('')
    for (let i = 0; i < chars.length; i++) {
      if (cancelled) break
      target.value += chars[i]
      await new Promise(r => setTimeout(r, Math.random() * speed + 20))
    }

    isTypingFlag.value = false
  }

  /**
   * 依次对 title、desc 执行打字机效果
   * @param titleText  标题原文
   * @param titleTarget  写入标题的 Ref
   * @param descText  描述原文
   * @param descTarget  写入描述的 Ref
   */
  async function start(
    titleText: string,
    titleTarget: Ref<string>,
    descText: string,
    descTarget: Ref<string>
  ) {
    cancelled = false
    titleTarget.value = ''
    descTarget.value = ''
    await typeText(titleText, titleTarget, isTypingTitle)
    if (!cancelled) {
      await typeText(descText, descTarget, isTypingDesc)
    }
  }

  /** 立即停止打字机效果 */
  function stop() {
    cancelled = true
    isTypingTitle.value = false
    isTypingDesc.value = false
  }

  return {
    isTypingTitle,
    isTypingDesc,
    start,
    stop
  }
}
