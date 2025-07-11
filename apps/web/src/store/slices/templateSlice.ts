import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface Template {
  id: string
  name: string
  description: string
  thumbnail: string
  category: string
  tags: string[]
  duration: number
  elements: any[]
}

interface TemplateState {
  templates: Template[]
  selectedTemplate: Template | null
  loading: boolean
  error: string | null
}

const initialState: TemplateState = {
  templates: [],
  selectedTemplate: null,
  loading: false,
  error: null,
}

const templateSlice = createSlice({
  name: 'template',
  initialState,
  reducers: {
    setTemplates: (state, action: PayloadAction<Template[]>) => {
      state.templates = action.payload
    },
    setSelectedTemplate: (state, action: PayloadAction<Template | null>) => {
      state.selectedTemplate = action.payload
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload
    },
  },
})

export const { setTemplates, setSelectedTemplate, setLoading, setError } = templateSlice.actions
export default templateSlice.reducer
