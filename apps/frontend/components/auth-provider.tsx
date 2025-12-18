"use client"

import { createContext, useContext, useEffect, useState, ReactNode } from "react"
import { useRouter, usePathname } from "next/navigation"
import { isAuthenticated, getAuthUser, type AuthUser } from "@/lib/auth"

interface AuthContextType {
  user: AuthUser | null
  isAuthenticated: boolean
  loading: boolean
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
  loading: true,
})

export function useAuth() {
  return useContext(AuthContext)
}

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    // Check authentication status
    const checkAuth = () => {
      const authUser = getAuthUser()
      const authenticated = isAuthenticated()
      
      setUser(authUser)
      setLoading(false)

      // Define public routes that don't require authentication
      const isLoginPage = pathname === '/login'
      const isPublicPage = 
        pathname?.startsWith('/verify') || 
        pathname?.startsWith('/waitlist/status') ||
        pathname === '/'
      
      // Only redirect if we're not already on a public page
      if (!authenticated && !isLoginPage && !isPublicPage) {
        // Only redirect if we're trying to access a protected route
        const isProtectedRoute = pathname?.startsWith('/contacts') || 
                                 pathname?.startsWith('/waitlist') ||
                                 pathname?.startsWith('/leads') ||
                                 pathname?.startsWith('/newsletter') ||
                                 pathname?.startsWith('/analytics') ||
                                 pathname?.startsWith('/gdpr')
        
        if (isProtectedRoute) {
          router.push('/login')
        }
      } else if (authenticated && isLoginPage) {
        // If logged in and on login page, redirect to dashboard
        router.push('/')
      }
    }

    checkAuth()
  }, [pathname, router])

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: isAuthenticated(), loading }}>
      {children}
    </AuthContext.Provider>
  )
}

