"use client"

import { useState } from "react"
import { Shield, Check, X, FileText, Info } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { DashboardSidebar } from "@/components/dashboard-sidebar"
import { DashboardHeader } from "@/components/dashboard-header"

type ConsentType =
  | "marketing"
  | "analytics"
  | "cookies_essential"
  | "cookies_functional"
  | "cookies_analytics"
  | "cookies_marketing"

interface ConsentState {
  marketing: boolean
  analytics: boolean
  cookies_essential: boolean
  cookies_functional: boolean
  cookies_analytics: boolean
  cookies_marketing: boolean
}

export default function GDPRConsentPage() {
  const [email, setEmail] = useState("")
  const [consent, setConsent] = useState<ConsentState>({
    marketing: false,
    analytics: false,
    cookies_essential: true, // Always enabled by default
    cookies_functional: false,
    cookies_analytics: false,
    cookies_marketing: false,
  })
  const [showPrivacyPolicy, setShowPrivacyPolicy] = useState(false)
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle")
  const [message, setMessage] = useState("")

  const handleConsentChange = (type: ConsentType, checked: boolean) => {
    setConsent((prev) => ({ ...prev, [type]: checked }))
  }

  const handleSavePreferences = async () => {
    if (!email) {
      setStatus("error")
      setMessage("Please enter your email address")
      return
    }

    setStatus("loading")

    try {
      // Save each consent type separately
      const consentTypes: ConsentType[] = Object.keys(consent) as ConsentType[]

      for (const type of consentTypes) {
        await fetch("/api/gdpr/consent", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email,
            consent_type: type,
            consent_given: consent[type],
          }),
        })
      }

      setStatus("success")
      setMessage("Your privacy preferences have been saved successfully!")

      // Reset after 5 seconds
      setTimeout(() => {
        setStatus("idle")
        setMessage("")
      }, 5000)
    } catch (error) {
      setStatus("error")
      setMessage("Failed to save preferences. Please try again.")
    }
  }

  const handleWithdrawConsent = async () => {
    if (!email) {
      setStatus("error")
      setMessage("Please enter your email address")
      return
    }

    setStatus("loading")

    try {
      // Withdraw all consents except essential cookies
      const consentTypes: ConsentType[] = Object.keys(consent) as ConsentType[]

      for (const type of consentTypes) {
        if (type !== "cookies_essential") {
          await fetch("/api/gdpr/consent", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              email,
              consent_type: type,
              consent_given: false,
            }),
          })
        }
      }

      // Update UI
      setConsent({
        marketing: false,
        analytics: false,
        cookies_essential: true,
        cookies_functional: false,
        cookies_analytics: false,
        cookies_marketing: false,
      })

      setStatus("success")
      setMessage("All consents have been withdrawn successfully!")

      setTimeout(() => {
        setStatus("idle")
        setMessage("")
      }, 5000)
    } catch (error) {
      setStatus("error")
      setMessage("Failed to withdraw consent. Please try again.")
    }
  }

  return (
    <div className="flex h-screen bg-background">
      <DashboardSidebar />

      <div className="flex-1 flex flex-col overflow-hidden">
        <DashboardHeader />

        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-3xl mx-auto space-y-6">
            <div>
              <h1 className="text-3xl font-bold text-foreground">Privacy Preferences</h1>
              <p className="text-muted-foreground mt-2">Manage your privacy and data consent preferences</p>
            </div>

            {status === "success" && (
              <Alert className="border-green-200 bg-green-50 text-green-800">
                <Check className="h-4 w-4" />
                <AlertDescription>{message}</AlertDescription>
              </Alert>
            )}

            {status === "error" && (
              <Alert className="border-red-200 bg-red-50 text-red-800">
                <X className="h-4 w-4" />
                <AlertDescription>{message}</AlertDescription>
              </Alert>
            )}

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-primary" />
                  Your Email Address
                </CardTitle>
                <CardDescription>Enter your email address to manage your consent preferences</CardDescription>
              </CardHeader>
              <CardContent>
                <Input
                  type="email"
                  placeholder="your.email@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="max-w-md"
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Marketing Communications</CardTitle>
                <CardDescription>Control how we communicate with you about our products and services</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start gap-3">
                  <Checkbox
                    id="marketing"
                    checked={consent.marketing}
                    onCheckedChange={(checked) => handleConsentChange("marketing", checked as boolean)}
                  />
                  <div className="flex-1">
                    <Label htmlFor="marketing" className="text-sm font-medium cursor-pointer">
                      Marketing Emails
                    </Label>
                    <p className="text-sm text-muted-foreground mt-1">
                      Receive updates about new features, promotions, and special offers
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Analytics & Performance</CardTitle>
                <CardDescription>Help us improve our services by sharing usage data</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start gap-3">
                  <Checkbox
                    id="analytics"
                    checked={consent.analytics}
                    onCheckedChange={(checked) => handleConsentChange("analytics", checked as boolean)}
                  />
                  <div className="flex-1">
                    <Label htmlFor="analytics" className="text-sm font-medium cursor-pointer">
                      Analytics Tracking
                    </Label>
                    <p className="text-sm text-muted-foreground mt-1">
                      Allow us to collect anonymous usage data to improve our platform
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Cookie Preferences</CardTitle>
                <CardDescription>Manage which cookies we can use on our website</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start gap-3 opacity-50">
                  <Checkbox id="cookies_essential" checked={consent.cookies_essential} disabled />
                  <div className="flex-1">
                    <Label htmlFor="cookies_essential" className="text-sm font-medium">
                      Essential Cookies (Required)
                    </Label>
                    <p className="text-sm text-muted-foreground mt-1">
                      Necessary for the website to function properly. Cannot be disabled.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Checkbox
                    id="cookies_functional"
                    checked={consent.cookies_functional}
                    onCheckedChange={(checked) => handleConsentChange("cookies_functional", checked as boolean)}
                  />
                  <div className="flex-1">
                    <Label htmlFor="cookies_functional" className="text-sm font-medium cursor-pointer">
                      Functional Cookies
                    </Label>
                    <p className="text-sm text-muted-foreground mt-1">
                      Remember your preferences and settings for a better experience
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Checkbox
                    id="cookies_analytics"
                    checked={consent.cookies_analytics}
                    onCheckedChange={(checked) => handleConsentChange("cookies_analytics", checked as boolean)}
                  />
                  <div className="flex-1">
                    <Label htmlFor="cookies_analytics" className="text-sm font-medium cursor-pointer">
                      Analytics Cookies
                    </Label>
                    <p className="text-sm text-muted-foreground mt-1">
                      Help us understand how visitors interact with our website
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Checkbox
                    id="cookies_marketing"
                    checked={consent.cookies_marketing}
                    onCheckedChange={(checked) => handleConsentChange("cookies_marketing", checked as boolean)}
                  />
                  <div className="flex-1">
                    <Label htmlFor="cookies_marketing" className="text-sm font-medium cursor-pointer">
                      Marketing Cookies
                    </Label>
                    <p className="text-sm text-muted-foreground mt-1">
                      Track your visits and show you relevant advertisements
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-muted bg-muted/20">
              <CardContent className="pt-6">
                <div className="flex items-start gap-3">
                  <Info className="h-5 w-5 text-primary mt-0.5 shrink-0" />
                  <div className="flex-1">
                    <p className="text-sm text-foreground">
                      For more information about how we collect and use your data, please read our{" "}
                      <button
                        onClick={() => setShowPrivacyPolicy(true)}
                        className="text-primary hover:underline font-medium"
                      >
                        Privacy Policy
                      </button>
                      .
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <div className="flex gap-4">
              <Button
                onClick={handleSavePreferences}
                disabled={status === "loading" || !email}
                className="min-w-[200px]"
              >
                {status === "loading" ? "Saving..." : "Save Preferences"}
              </Button>

              <Button variant="outline" onClick={handleWithdrawConsent} disabled={status === "loading" || !email}>
                Withdraw All Consent
              </Button>
            </div>
          </div>
        </main>
      </div>

      <Dialog open={showPrivacyPolicy} onOpenChange={setShowPrivacyPolicy}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Privacy Policy
            </DialogTitle>
            <DialogDescription>Last updated: December 19, 2025</DialogDescription>
          </DialogHeader>

          <div className="space-y-4 text-sm">
            <section>
              <h3 className="font-semibold text-base mb-2">1. Information We Collect</h3>
              <p className="text-muted-foreground">
                We collect information you provide directly to us, including your name, email address, and any other
                information you choose to provide. We also automatically collect certain information about your device
                when you use our services.
              </p>
            </section>

            <section>
              <h3 className="font-semibold text-base mb-2">2. How We Use Your Information</h3>
              <p className="text-muted-foreground">
                We use the information we collect to provide, maintain, and improve our services, communicate with you,
                and comply with legal obligations. We process your personal data based on your consent, contractual
                necessity, and our legitimate interests.
              </p>
            </section>

            <section>
              <h3 className="font-semibold text-base mb-2">3. Data Sharing and Disclosure</h3>
              <p className="text-muted-foreground">
                We do not sell your personal information. We may share your information with service providers who
                perform services on our behalf, when required by law, or with your consent.
              </p>
            </section>

            <section>
              <h3 className="font-semibold text-base mb-2">4. Your Rights Under GDPR</h3>
              <p className="text-muted-foreground">
                You have the right to access, correct, delete, or restrict the use of your personal data. You can also
                object to processing, request data portability, and withdraw consent at any time. To exercise these
                rights, please contact us at privacy@example.com.
              </p>
            </section>

            <section>
              <h3 className="font-semibold text-base mb-2">5. Cookies and Tracking</h3>
              <p className="text-muted-foreground">
                We use cookies and similar technologies to collect information about your browsing activities. You can
                control cookie preferences through your browser settings and our consent management tool.
              </p>
            </section>

            <section>
              <h3 className="font-semibold text-base mb-2">6. Data Security</h3>
              <p className="text-muted-foreground">
                We implement appropriate technical and organizational measures to protect your personal data against
                unauthorized access, alteration, disclosure, or destruction.
              </p>
            </section>

            <section>
              <h3 className="font-semibold text-base mb-2">7. Contact Us</h3>
              <p className="text-muted-foreground">
                If you have any questions about this Privacy Policy or our data practices, please contact us at:
              </p>
              <p className="text-muted-foreground mt-2">
                Email: privacy@example.com
                <br />
                Address: 123 Privacy Street, Data City, DC 12345
              </p>
            </section>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
