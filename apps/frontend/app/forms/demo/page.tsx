"use client"

import * as React from "react"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  FormInput,
  FormSelect,
  FormTextarea,
  FormCheckbox,
  FormRadio,
  FormDatePicker,
  FormFileUpload,
  FormRating,
  FormSwitch,
  FormSlider,
} from "@/components/forms"
import { Mail, User, Lock } from "lucide-react"

const formSchema = z.object({
  email: z.string().email("Invalid email address"),
  username: z.string().min(3, "Username must be at least 3 characters"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  bio: z.string().max(500, "Bio must be less than 500 characters"),
  country: z.string().min(1, "Please select a country"),
  interests: z.array(z.string()).min(1, "Select at least one interest"),
  notifications: z.boolean(),
  theme: z.string(),
  birthdate: z.date().optional(),
  avatar: z.array(z.any()).optional(),
  rating: z.number().min(1, "Please provide a rating"),
  newsletter: z.boolean(),
  volume: z.array(z.number()),
})

type FormData = z.infer<typeof formSchema>

export default function FormsDemoPage() {
  const [isSubmitting, setIsSubmitting] = React.useState(false)
  const [formData, setFormData] = React.useState<FormData>({
    email: "",
    username: "",
    password: "",
    bio: "",
    country: "",
    interests: [],
    notifications: false,
    theme: "",
    rating: 0,
    newsletter: false,
    volume: [50],
  })
  const [errors, setErrors] = React.useState<Record<string, string>>({})

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setErrors({})

    try {
      await formSchema.parseAsync(formData)
      console.log("Form data:", formData)
      alert("Form submitted successfully!")
    } catch (error) {
      if (error instanceof z.ZodError) {
        const newErrors: Record<string, string> = {}
        error.errors.forEach((err) => {
          if (err.path) {
            newErrors[err.path[0]] = err.message
          }
        })
        setErrors(newErrors)
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="container mx-auto py-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Form Components Library</h1>
        <p className="text-muted-foreground">
          A comprehensive collection of reusable form components with validation, accessibility, and consistent styling.
        </p>
      </div>

      <Tabs defaultValue="demo" className="space-y-6">
        <TabsList>
          <TabsTrigger value="demo">Interactive Demo</TabsTrigger>
          <TabsTrigger value="examples">Individual Examples</TabsTrigger>
        </TabsList>

        <TabsContent value="demo">
          <Card>
            <CardHeader>
              <CardTitle>Complete Form Example</CardTitle>
              <CardDescription>All form components integrated with Zod validation</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid gap-6 md:grid-cols-2">
                  <FormInput
                    label="Email"
                    type="email"
                    placeholder="john@example.com"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    error={errors.email}
                    isRequired
                    leftIcon={<Mail className="h-4 w-4" />}
                  />
                  <FormInput
                    label="Username"
                    placeholder="johndoe"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    error={errors.username}
                    isRequired
                    leftIcon={<User className="h-4 w-4" />}
                  />
                </div>

                <FormInput
                  label="Password"
                  type="password"
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  error={errors.password}
                  isRequired
                  leftIcon={<Lock className="h-4 w-4" />}
                  helperText="Must be at least 8 characters"
                />

                <FormTextarea
                  label="Bio"
                  placeholder="Tell us about yourself..."
                  value={formData.bio}
                  onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                  error={errors.bio}
                  showCharCount
                  maxLength={500}
                  rows={4}
                />

                <FormSelect
                  label="Country"
                  placeholder="Select your country"
                  options={[
                    { label: "United States", value: "us" },
                    { label: "United Kingdom", value: "uk" },
                    { label: "Canada", value: "ca" },
                    { label: "Australia", value: "au" },
                    { label: "Germany", value: "de" },
                  ]}
                  value={formData.country}
                  onChange={(value) => setFormData({ ...formData, country: value as string })}
                  error={errors.country}
                  isRequired
                />

                <FormSelect
                  label="Interests"
                  placeholder="Select your interests"
                  options={[
                    { label: "Technology", value: "tech" },
                    { label: "Design", value: "design" },
                    { label: "Business", value: "business" },
                    { label: "Marketing", value: "marketing" },
                    { label: "Development", value: "dev" },
                  ]}
                  value={formData.interests}
                  onChange={(value) => setFormData({ ...formData, interests: value as string[] })}
                  error={errors.interests}
                  multiSelect
                  isRequired
                />

                <FormRadio
                  label="Theme Preference"
                  options={[
                    { label: "Light", value: "light", description: "Light mode theme" },
                    { label: "Dark", value: "dark", description: "Dark mode theme" },
                    { label: "System", value: "system", description: "Follow system preference" },
                  ]}
                  value={formData.theme}
                  onChange={(value) => setFormData({ ...formData, theme: value })}
                  error={errors.theme}
                  orientation="horizontal"
                />

                <FormDatePicker
                  label="Birth Date"
                  value={formData.birthdate}
                  onChange={(date) => setFormData({ ...formData, birthdate: date as Date })}
                  error={errors.birthdate}
                />

                <FormFileUpload
                  label="Profile Avatar"
                  accept="image/*"
                  value={formData.avatar as File[]}
                  onChange={(files) => setFormData({ ...formData, avatar: files })}
                  error={errors.avatar}
                  maxSize={2}
                  helperText="Upload a profile picture (max 2MB)"
                />

                <FormRating
                  label="Rate Your Experience"
                  value={formData.rating}
                  onChange={(rating) => setFormData({ ...formData, rating })}
                  error={errors.rating}
                  isRequired
                  allowHalf
                />

                <FormSlider
                  label="Notification Volume"
                  value={formData.volume}
                  onChange={(value) => setFormData({ ...formData, volume: value })}
                  min={0}
                  max={100}
                  step={5}
                  formatValue={(val) => `${val}%`}
                  helperText="Adjust notification sound level"
                />

                <div className="space-y-4">
                  <FormCheckbox
                    label="Enable Notifications"
                    description="Receive email notifications about your account activity"
                    checked={formData.notifications}
                    onCheckedChange={(checked) => setFormData({ ...formData, notifications: checked })}
                    error={errors.notifications}
                  />

                  <FormSwitch
                    label="Newsletter Subscription"
                    description="Receive our weekly newsletter with updates and tips"
                    checked={formData.newsletter}
                    onCheckedChange={(checked) => setFormData({ ...formData, newsletter: checked })}
                    error={errors.newsletter}
                  />
                </div>

                <div className="flex gap-3">
                  <Button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? "Submitting..." : "Submit Form"}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setFormData({
                        email: "",
                        username: "",
                        password: "",
                        bio: "",
                        country: "",
                        interests: [],
                        notifications: false,
                        theme: "",
                        rating: 0,
                        newsletter: false,
                        volume: [50],
                      })
                      setErrors({})
                    }}
                  >
                    Reset
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="examples">
          <div className="grid gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Input Components</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <FormInput label="Default Input" placeholder="Enter text..." />
                <FormInput label="With Error" placeholder="Enter text..." error="This field is required" />
                <FormInput label="Disabled" placeholder="Enter text..." disabled />
                <FormInput label="Loading" placeholder="Enter text..." isLoading />
                <FormInput label="With Icons" placeholder="Search..." leftIcon={<User className="h-4 w-4" />} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Selection Components</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <FormSelect
                  label="Single Select"
                  options={[
                    { label: "Option 1", value: "1" },
                    { label: "Option 2", value: "2" },
                  ]}
                />
                <FormSelect
                  label="Multi Select"
                  options={[
                    { label: "Option 1", value: "1" },
                    { label: "Option 2", value: "2" },
                    { label: "Option 3", value: "3" },
                  ]}
                  multiSelect
                />
                <FormRadio
                  label="Radio Group"
                  options={[
                    { label: "Option A", value: "a" },
                    { label: "Option B", value: "b" },
                  ]}
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Interactive Components</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <FormRating label="Star Rating" />
                <FormSlider label="Range Slider" />
                <FormCheckbox label="Checkbox" description="With description" />
                <FormSwitch label="Toggle Switch" description="Enable or disable feature" />
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
