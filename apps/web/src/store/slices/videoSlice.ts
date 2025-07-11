import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface Video {
  id: string
  title: string
  description?: string
  url: string
  thumbnail?: string
  duration: number
  createdAt: string
  status: 'processing' | 'completed' | 'failed'
}

interface VideoState {
  videos: Video[]
  currentVideo: Video | null
  loading: boolean
  error: string | null
  uploadProgress: number
}

const initialState: VideoState = {
  videos: [],
  currentVideo: null,
  loading: false,
  error: null,
  uploadProgress: 0,
}

const videoSlice = createSlice({
  name: 'video',
  initialState,
  reducers: {
    setVideos: (state, action: PayloadAction<Video[]>) => {
      state.videos = action.payload
    },
    addVideo: (state, action: PayloadAction<Video>) => {
      state.videos.unshift(action.payload)
    },
    updateVideo: (state, action: PayloadAction<Video>) => {
      const index = state.videos.findIndex(v => v.id === action.payload.id)
      if (index !== -1) {
        state.videos[index] = action.payload
      }
    },
    setCurrentVideo: (state, action: PayloadAction<Video | null>) => {
      state.currentVideo = action.payload
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload
    },
    setUploadProgress: (state, action: PayloadAction<number>) => {
      state.uploadProgress = action.payload
    },
  },
})

export const {
  setVideos,
  addVideo,
  updateVideo,
  setCurrentVideo,
  setLoading,
  setError,
  setUploadProgress,
} = videoSlice.actions

export default videoSlice.reducer
