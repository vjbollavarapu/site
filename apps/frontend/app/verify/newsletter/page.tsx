"use client"

import { useEffect, useState, Suspense } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { CheckCircle2, XCircle, Loader2, Mail } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"

type VerificationState = "loading" | "success" | "error" | "invalid"

function NewsletterVerificationContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const [state, setState] = useState<VerificationState>("loading")
  const [email, setEmail] = useState<string>("")
  const [isResending, setIsResending] = useState(false)
  const [resendSuccess, setResendSuccess] = useState(false)

  useEffect(() => {
    const token = searchParams.get("token")
    const emailParam = searchParams.get("email")

    if (emailParam) {
      setEmail(emailParam)
    }

    if (!token) {
      setState("invalid")
      return
    }

    verifyEmail(token, emailParam || "")
  }, [searchParams])

  const verifyEmail = async (token: string, emailParam: string) => {
    try {
      const response = await fetch("/api/newsletter/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, email: emailParam }),
      })

      if (response.ok) {
        const data = await response.json()
        setEmail(data.email || emailParam)
        setState("success")
      } else if (response.status === 400) {
        setState("invalid")
      } else if (response.status === 404) {
        setState("error")
      } else {
        setState("error")
      }
    } catch (error) {
      console.error("[v0] Verification error:", error)
      setState("error")
    }
  }

  const handleResendVerification = async () => {
    if (!email) return

    setIsResending(true)
    setResendSuccess(false)

    try {
      const response = await fetch("/api/newsletter/resend-verification", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      })

      if (response.ok) {
        setResendSuccess(true)
      }
    } catch (error) {
      console.error("[v0] Resend error:", error)
    } finally {
      setIsResending(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
            {state === "loading" && <Loader2 className="h-6 w-6 animate-spin text-primary" />}
            {state === "success" && <CheckCircle2 className="h-6 w-6 text-green-600" />}
            {(state === "error" || state === "invalid") && <XCircle className="h-6 w-6 text-destructive" />}
          </div>
          <CardTitle>
            {state === "loading" && "Verifying Your Email"}
            {state === "success" && "Subscription Confirmed!"}
            {(state === "error" || state === "invalid") && "Verification Failed"}
          </CardTitle>
          <CardDescription>
            {state === "loading" && "Please wait while we confirm your subscription..."}
            {state === "success" && "You're now subscribed to our newsletter."}
            {state === "invalid" && "The verification link is invalid or has expired."}
            {state === "error" && "We couldn't verify your email. Please try again."}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {state === "success" && (
            <>
              <Alert className="bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-900">
                <CheckCircle2 className="h-4 w-4 text-green-600" />
                <AlertDescription className="text-green-800 dark:text-green-200">
                  Your email has been successfully verified. You'll start receiving our newsletter soon!
                </AlertDescription>
              </Alert>
              {email && (
                <p className="text-sm text-muted-foreground text-center">
                  <span className="font-medium text-foreground">{email}</span> is now subscribed.
                </p>
              )}
              <div className="bg-muted/50 border border-border rounded-lg p-4 space-y-2">
                <h4 className="font-medium text-sm">What's next?</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• You'll receive our weekly newsletter</li>
                  <li>• Get exclusive updates and insights</li>
                  <li>• Unsubscribe anytime from any email</li>
                </ul>
              </div>
              <Button onClick={() => router.push("/")} className="w-full">
                Return to Home
              </Button>
            </>
          )}

          {(state === "invalid" || state === "error") && (
            <>
              <Alert variant="destructive">
                <XCircle className="h-4 w-4" />
                <AlertDescription>
                  {state === "invalid" &&
                    "This verification link is invalid or has expired. Please request a new verification email."}
                  {state === "error" &&
                    "Something went wrong during verification. Please try again or contact support."}
                </AlertDescription>
              </Alert>

              {email && (
                <div className="space-y-3">
                  <p className="text-sm text-muted-foreground text-center">
                    Email: <span className="font-medium text-foreground">{email}</span>
                  </p>
                  {resendSuccess && (
                    <Alert className="bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-900">
                      <Mail className="h-4 w-4 text-green-600" />
                      <AlertDescription className="text-green-800 dark:text-green-200">
                        Verification email sent! Check your inbox.
                      </AlertDescription>
                    </Alert>
                  )}
                  <Button
                    onClick={handleResendVerification}
                    disabled={isResending}
                    variant="outline"
                    className="w-full bg-transparent"
                  >
                    {isResending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Resend Verification Email
                  </Button>
                </div>
              )}

              <Button onClick={() => router.push("/")} variant="secondary" className="w-full">
                Return to Home
              </Button>
            </>
          )}

          {state === "loading" && (
            <div className="flex justify-center py-4">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default function NewsletterVerificationPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-background">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      }
    >
      <NewsletterVerificationContent />
    </Suspense>
  )
}
