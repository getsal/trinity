import { describe, expect, it } from 'vitest'
import {
  defaultModelForRuntime,
  isModelCompatibleWithRuntime,
  presetModelsForRuntime,
} from '../../src/utils/runtime-models'

describe('runtime model catalog', () => {
  it('shows Codex-only presets for Codex agents', () => {
    expect(presetModelsForRuntime('codex').map(({ value }) => value)).toEqual([
      'gpt-5.1-codex',
      'gpt-5.1-codex-max',
      'gpt-5-codex',
    ])
    expect(defaultModelForRuntime('codex')).toBe('gpt-5.1-codex')
  })

  it('keeps saved models within their runtime family', () => {
    expect(isModelCompatibleWithRuntime('claude-sonnet-4-6', 'codex')).toBe(false)
    expect(isModelCompatibleWithRuntime('gpt-5.1-codex', 'claude-code')).toBe(false)
    expect(isModelCompatibleWithRuntime('gemini-3-flash', 'gemini-cli')).toBe(true)
    expect(isModelCompatibleWithRuntime('custom-provider-model', 'codex')).toBe(true)
  })
})
