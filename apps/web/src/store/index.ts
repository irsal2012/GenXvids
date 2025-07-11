import { configureStore } from '@reduxjs/toolkit'
import authSlice from './slices/authSlice'
import videoSlice from './slices/videoSlice'
import templateSlice from './slices/templateSlice'
import projectSlice from './slices/projectSlice'

export const store = configureStore({
  reducer: {
    auth: authSlice,
    video: videoSlice,
    template: templateSlice,
    project: projectSlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
