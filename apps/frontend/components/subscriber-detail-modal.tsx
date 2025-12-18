"use client"

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import type { Subscriber } from "@/types/subscriber"
import { format } from "date-fns"
import { Mail, MousePointer, Check, X, Calendar, MapPin } from "lucide-react"

interface SubscriberDetailModalProps {
  subscriber: Subscriber
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function SubscriberDetailModal({ subscriber, open, onOpenChange }: SubscriberDetailModalProps) {
  const statusVariants: Record<string, "default" | "secondary" | "destructive"> = {
    subscribed: "default",
    unsubscribed: "secondary",
    bounced: "destructive",
    complained: "destructive",
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl">Subscriber Details</DialogTitle>
        </DialogHeader>

        <Tabs defaultValue="info" className="mt-4">
          <TabsList>
            <TabsTrigger value="info">Information</TabsTrigger>
            <TabsTrigger value="engagement">Engagement</TabsTrigger>
            <TabsTrigger value="timeline">Timeline</TabsTrigger>
          </TabsList>

          <TabsContent value="info" className="space-y-6 mt-6">
            {/* Basic Info */}
            <Card className="p-6">
              <h3 className="font-semibold text-lg mb-4">Basic Information</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Email</p>
                  <p className="font-medium">{subscriber.email}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Name</p>
                  <p className="font-medium">{subscriber.name || "-"}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Status</p>
                  <Badge variant={statusVariants[subscriber.status]} className="mt-1">
                    {subscriber.status}
                  </Badge>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Verified</p>
                  <div className="flex items-center gap-2 mt-1">
                    {subscriber.verified ? (
                      <>
                        <Check className="h-4 w-4 text-green-500" />
                        <span className="text-sm">Verified</span>
                      </>
                    ) : (
                      <>
                        <X className="h-4 w-4 text-red-500" />
                        <span className="text-sm">Not Verified</span>
                      </>
                    )}
                  </div>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Source</p>
                  <p className="font-medium capitalize">{subscriber.source}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Subscribed At</p>
                  <p className="font-medium">{format(new Date(subscriber.subscribedAt), "PPP")}</p>
                </div>
                {subscriber.location && (
                  <div>
                    <p className="text-sm text-muted-foreground">Location</p>
                    <div className="flex items-center gap-2 mt-1">
                      <MapPin className="h-4 w-4 text-muted-foreground" />
                      <p className="font-medium">{subscriber.location}</p>
                    </div>
                  </div>
                )}
                {subscriber.lastEmailSent && (
                  <div>
                    <p className="text-sm text-muted-foreground">Last Email Sent</p>
                    <p className="font-medium">{format(new Date(subscriber.lastEmailSent), "PPP")}</p>
                  </div>
                )}
              </div>
            </Card>

            {/* Email Preferences */}
            <Card className="p-6">
              <h3 className="font-semibold text-lg mb-4">Email Preferences</h3>
              <div className="space-y-3">
                {subscriber.preferences.map((pref) => (
                  <div key={pref} className="flex items-center justify-between">
                    <span className="capitalize">{pref.replace("_", " ")}</span>
                    <Check className="h-4 w-4 text-green-500" />
                  </div>
                ))}
              </div>
            </Card>

            {/* Unsubscribe Reason */}
            {subscriber.unsubscribeReason && (
              <Card className="p-6">
                <h3 className="font-semibold text-lg mb-4">Unsubscribe Reason</h3>
                <p className="text-muted-foreground">{subscriber.unsubscribeReason}</p>
                {subscriber.unsubscribedAt && (
                  <p className="text-sm text-muted-foreground mt-2">
                    Unsubscribed on {format(new Date(subscriber.unsubscribedAt), "PPP")}
                  </p>
                )}
              </Card>
            )}
          </TabsContent>

          <TabsContent value="engagement" className="space-y-6 mt-6">
            <Card className="p-6">
              <h3 className="font-semibold text-lg mb-4">Engagement Statistics</h3>
              <div className="grid grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="flex items-center justify-center gap-2 mb-2">
                    <Mail className="h-5 w-5 text-blue-500" />
                  </div>
                  <p className="text-3xl font-bold">{subscriber.engagement.emailsSent}</p>
                  <p className="text-sm text-muted-foreground">Emails Sent</p>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center gap-2 mb-2">
                    <Mail className="h-5 w-5 text-green-500" />
                  </div>
                  <p className="text-3xl font-bold">{subscriber.engagement.opens}</p>
                  <p className="text-sm text-muted-foreground">Opens</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {((subscriber.engagement.opens / subscriber.engagement.emailsSent) * 100).toFixed(1)}% rate
                  </p>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center gap-2 mb-2">
                    <MousePointer className="h-5 w-5 text-purple-500" />
                  </div>
                  <p className="text-3xl font-bold">{subscriber.engagement.clicks}</p>
                  <p className="text-sm text-muted-foreground">Clicks</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {((subscriber.engagement.clicks / subscriber.engagement.emailsSent) * 100).toFixed(1)}% rate
                  </p>
                </div>
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="font-semibold text-lg mb-4">Last Engagement</h3>
              <div className="space-y-3">
                {subscriber.engagement.lastOpened && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Last Opened</span>
                    <span className="font-medium">{format(new Date(subscriber.engagement.lastOpened), "PPP")}</span>
                  </div>
                )}
                {subscriber.engagement.lastClicked && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Last Clicked</span>
                    <span className="font-medium">{format(new Date(subscriber.engagement.lastClicked), "PPP")}</span>
                  </div>
                )}
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="timeline" className="space-y-4 mt-6">
            <Card className="p-6">
              <h3 className="font-semibold text-lg mb-4">Subscription Timeline</h3>
              <div className="space-y-4">
                {subscriber.timeline.map((event, index) => (
                  <div key={index} className="flex gap-4">
                    <div className="flex flex-col items-center">
                      <div className="h-2 w-2 rounded-full bg-primary" />
                      {index !== subscriber.timeline.length - 1 && <div className="w-px h-full bg-border" />}
                    </div>
                    <div className="flex-1 pb-4">
                      <div className="flex items-center gap-2 mb-1">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm text-muted-foreground">
                          {format(new Date(event.date), "PPP 'at' p")}
                        </span>
                      </div>
                      <p className="font-medium">{event.event}</p>
                      {event.details && <p className="text-sm text-muted-foreground mt-1">{event.details}</p>}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </TabsContent>
        </Tabs>

        <div className="flex justify-end gap-2 mt-6">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
