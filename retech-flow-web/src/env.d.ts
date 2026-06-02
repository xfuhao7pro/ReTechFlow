/// <reference types="vite/client" />

declare module 'vue3-puzzle-vcode' {
  import { DefineComponent } from 'vue'
  
  export interface VcodeProps {
    id?: string
    show?: boolean
    canvasWidth?: number
    canvasHeight?: number
    puzzleScale?: number
    sliderSize?: number
    range?: number
    imgs?: string[]
    successText?: string
    failText?: string
    sliderText?: string
  }

  export interface VcodeEmits {
    (e: 'success', deviation: number): void
    (e: 'fail', deviation: number): void
    (e: 'close'): void
  }

  const Vcode: DefineComponent<VcodeProps, {}, any, any, any, any, any, VcodeEmits>
  export default Vcode
}