
export function isAutoSaveMode(mode: string): boolean {
  return ['createBatch', 'createNote', 'editDraft'].includes(mode)
}

