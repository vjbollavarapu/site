"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { isAuthenticated, getAuthUser, logout as authLogout, type AuthUser } from "@/lib/auth"

export function useAuth() {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const checkAuth = () => {
      const authUser = getAuthUser()
      setUser(authUser)
      setLoading(false)
    }
    checkAuth()
  }, [])

  const logout = () => {
    authLogout()
    setUser(null)
    router.push('/login')
    router.refresh()
  }

  return {
    user,
    isAuthenticated: isAuthenticated(),
    loading,
    logout,
  }
}

