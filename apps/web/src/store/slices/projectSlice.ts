import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface Project {
  id: string
  name: string
  description?: string
  templateId?: string
  settings: any
  createdAt: string
  updatedAt: string
}

interface ProjectState {
  projects: Project[]
  currentProject: Project | null
  loading: boolean
  error: string | null
}

const initialState: ProjectState = {
  projects: [],
  currentProject: null,
  loading: false,
  error: null,
}

const projectSlice = createSlice({
  name: 'project',
  initialState,
  reducers: {
    setProjects: (state, action: PayloadAction<Project[]>) => {
      state.projects = action.payload
    },
    addProject: (state, action: PayloadAction<Project>) => {
      state.projects.unshift(action.payload)
    },
    updateProject: (state, action: PayloadAction<Project>) => {
      const index = state.projects.findIndex(p => p.id === action.payload.id)
      if (index !== -1) {
        state.projects[index] = action.payload
      }
    },
    setCurrentProject: (state, action: PayloadAction<Project | null>) => {
      state.currentProject = action.payload
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload
    },
  },
})

export const {
  setProjects,
  addProject,
  updateProject,
  setCurrentProject,
  setLoading,
  setError,
} = projectSlice.actions

export default projectSlice.reducer
