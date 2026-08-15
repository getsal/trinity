const CLAUDE_MODELS = [
  { value: 'claude-fable-5', label: 'Claude Fable 5', note: 'Most capable — longest tasks (latest)' },
  { value: 'claude-sonnet-5', label: 'Claude Sonnet 5', note: 'Fast + smart, 1M context (latest)' },
  { value: 'claude-opus-4-8', label: 'Claude Opus 4.8', note: 'Most capable Opus' },
  { value: 'claude-opus-4-7', label: 'Claude Opus 4.7', note: 'Current' },
  { value: 'claude-opus-4-6', label: 'Claude Opus 4.6', note: 'Current' },
  { value: 'claude-sonnet-4-6', label: 'Claude Sonnet 4.6', note: 'Fast + smart' },
  { value: 'claude-haiku-4-5-20251001', label: 'Claude Haiku 4.5', note: 'Fastest, cheapest' },
  { value: 'claude-opus-4-5-20251101', label: 'Claude Opus 4.5', note: 'Legacy' },
  { value: 'claude-sonnet-4-5-20250929', label: 'Claude Sonnet 4.5', note: 'Legacy' },
]

const CODEX_MODELS = [
  { value: 'gpt-5.1-codex', label: 'GPT-5.1 Codex', note: 'Codex default' },
  { value: 'gpt-5.1-codex-max', label: 'GPT-5.1 Codex Max', note: 'Maximum reasoning' },
  { value: 'gpt-5-codex', label: 'GPT-5 Codex', note: 'Legacy Codex' },
]

const GEMINI_MODELS = [
  { value: 'gemini-3-pro', label: 'Gemini 3 Pro', note: 'Most capable' },
  { value: 'gemini-3-flash', label: 'Gemini 3 Flash', note: 'Fast default' },
  { value: 'gemini-2.5-pro', label: 'Gemini 2.5 Pro', note: 'Previous generation' },
  { value: 'gemini-2.5-flash', label: 'Gemini 2.5 Flash', note: 'Previous generation' },
]

export function runtimeModelFamily(runtime) {
  const normalized = (runtime || 'claude-code').toLowerCase()
  if (normalized === 'codex') return 'codex'
  if (normalized === 'gemini' || normalized === 'gemini-cli') return 'gemini'
  return 'claude'
}

export function presetModelsForRuntime(runtime) {
  switch (runtimeModelFamily(runtime)) {
    case 'codex':
      return CODEX_MODELS
    case 'gemini':
      return GEMINI_MODELS
    default:
      return CLAUDE_MODELS
  }
}

export function defaultModelForRuntime(runtime) {
  return presetModelsForRuntime(runtime)[0].value
}

export function isModelCompatibleWithRuntime(model, runtime) {
  if (!model) return true

  const family = runtimeModelFamily(runtime)
  const normalized = model.toLowerCase()
  const modelFamily = normalized.startsWith('gemini-')
    ? 'gemini'
    : normalized.startsWith('gpt-') || normalized.startsWith('codex-')
      ? 'codex'
      : normalized.startsWith('claude-') || /^(sonnet|opus|haiku|fable)(\[1m\])?$/.test(normalized)
        ? 'claude'
        : null

  return modelFamily === null || modelFamily === family
}
