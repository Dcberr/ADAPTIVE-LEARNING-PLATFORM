"use client"

import { useMemo, useState } from "react"
import { Forward, Mail, MailOpen, Reply, Search, Trash2 } from "lucide-react"

import { messages } from "@/data/lms/mockData"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

type MessageItem = (typeof messages)[number]

function MessageListItem({
  message,
  isSelected,
  onClick,
}: {
  message: MessageItem
  isSelected: boolean
  onClick: () => void
}) {
  const messageDate = new Date(message.date)

  return (
    <Card
      className={isSelected ? "cursor-pointer border-blue-500 bg-blue-50" : "cursor-pointer hover:border-blue-300"}
      onClick={onClick}
    >
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-full bg-blue-100">
            <span className="font-semibold text-blue-600">{message.sender.charAt(0)}</span>
          </div>
          <div className="min-w-0 flex-1">
            <div className="mb-1 flex items-start justify-between">
              <p className={message.read ? "truncate text-sm font-medium" : "truncate text-sm font-semibold"}>
                {message.sender}
              </p>
              {!message.read ? <Badge className="shrink-0 bg-blue-600 text-white">New</Badge> : null}
            </div>
            <h4 className={message.read ? "truncate text-sm" : "truncate text-sm font-semibold"}>{message.subject}</h4>
            <p className="mt-1 line-clamp-2 text-xs text-gray-500">{message.preview}</p>
            <p className="mt-1 text-xs text-gray-400">
              {messageDate.toLocaleDateString("vi-VN", { month: "short", day: "numeric" })}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default function MessagesPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedMessage, setSelectedMessage] = useState<MessageItem | null>(null)

  const unreadMessages = messages.filter((message) => !message.read)

  const filteredMessages = useMemo(
    () =>
      messages.filter((message) => {
        const text = `${message.sender} ${message.subject} ${message.preview}`.toLowerCase()
        return text.includes(searchQuery.toLowerCase())
      }),
    [searchQuery]
  )

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Messages</h1>
          <p className="mt-1 text-sm text-gray-500">Communicate with instructors and classmates</p>
        </div>
        <Button>
          <Mail className="mr-2 size-4" />
          Compose
        </Button>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-gray-400" />
        <Input
          type="search"
          placeholder="Search messages..."
          className="pl-10"
          value={searchQuery}
          onChange={(event) => setSearchQuery(event.target.value)}
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-1">
          <Tabs defaultValue="all" className="w-full">
            <TabsList className="w-full">
              <TabsTrigger value="all" className="flex-1">
                All ({messages.length})
              </TabsTrigger>
              <TabsTrigger value="unread" className="flex-1">
                Unread ({unreadMessages.length})
              </TabsTrigger>
            </TabsList>

            <TabsContent value="all" className="mt-4 space-y-2">
              {filteredMessages.map((message) => (
                <MessageListItem
                  key={message.id}
                  message={message}
                  isSelected={selectedMessage?.id === message.id}
                  onClick={() => setSelectedMessage(message)}
                />
              ))}
            </TabsContent>

            <TabsContent value="unread" className="mt-4 space-y-2">
              {unreadMessages.length === 0 ? (
                <Card className="p-8 text-center">
                  <MailOpen className="mx-auto mb-3 size-12 text-gray-400" />
                  <p className="text-sm text-gray-500">No unread messages</p>
                </Card>
              ) : (
                unreadMessages.map((message) => (
                  <MessageListItem
                    key={message.id}
                    message={message}
                    isSelected={selectedMessage?.id === message.id}
                    onClick={() => setSelectedMessage(message)}
                  />
                ))
              )}
            </TabsContent>
          </Tabs>
        </div>

        <div className="lg:col-span-2">
          {selectedMessage ? (
            <Card>
              <CardContent className="p-6">
                <div className="mb-4 flex items-start justify-between">
                  <div>
                    <h2 className="mb-2 text-xl font-semibold">{selectedMessage.subject}</h2>
                    <div className="flex items-center gap-2">
                      <div className="flex size-10 items-center justify-center rounded-full bg-blue-100">
                        <span className="font-semibold text-blue-600">{selectedMessage.sender.charAt(0)}</span>
                      </div>
                      <div>
                        <p className="text-sm font-medium">{selectedMessage.sender}</p>
                        <p className="text-xs text-gray-500">
                          {new Date(selectedMessage.date).toLocaleDateString("vi-VN", {
                            month: "short",
                            day: "numeric",
                            hour: "numeric",
                            minute: "2-digit",
                          })}
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="ghost" size="icon">
                      <Reply className="size-4" />
                    </Button>
                    <Button variant="ghost" size="icon">
                      <Forward className="size-4" />
                    </Button>
                    <Button variant="ghost" size="icon">
                      <Trash2 className="size-4 text-red-600" />
                    </Button>
                  </div>
                </div>

                <div className="border-t border-gray-200 pt-4">
                  <p className="leading-relaxed text-gray-700">{selectedMessage.preview}</p>
                </div>

                <div className="mt-6 border-t border-gray-200 pt-4">
                  <Button className="w-full sm:w-auto">
                    <Reply className="mr-2 size-4" />
                    Reply
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card className="h-full">
              <CardContent className="flex h-96 items-center justify-center">
                <div className="text-center">
                  <Mail className="mx-auto mb-4 size-16 text-gray-400" />
                  <p className="text-gray-500">Select a message to read</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
