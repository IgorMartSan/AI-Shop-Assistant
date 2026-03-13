import Link from "next/link"
import {
  RiDatabase2Line,
  RiHomeOfficeLine,
  RiLayoutGridLine,
  RiRobot2Line,
  RiSettings3Line,
} from "@remixicon/react"

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import { Badge } from "@/components/ui/badge"

const mainItems = [
  { title: "Visao geral", href: "#overview", icon: RiHomeOfficeLine, active: true },
  { title: "Colecoes", href: "#collections", icon: RiDatabase2Line },
  { title: "Fluxos", href: "#flows", icon: RiLayoutGridLine },
]

const supportItems = [
  { title: "Assistente", href: "#assistant", icon: RiRobot2Line },
  { title: "Configuracoes", href: "#settings", icon: RiSettings3Line },
]

export function AppSidebar() {
  return (
    <Sidebar>
      <SidebarHeader>
        <div className="flex size-11 items-center justify-center rounded-2xl bg-sidebar-primary text-sidebar-primary-foreground">
          <RiRobot2Line className="size-5" />
        </div>
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold">AI Shop Assistant</p>
          <p className="text-xs text-sidebar-foreground/70">Painel operacional</p>
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Navegacao</SidebarGroupLabel>
          <SidebarMenu>
            {mainItems.map((item) => (
              <SidebarMenuItem key={item.title}>
                <SidebarMenuButton asChild isActive={item.active}>
                  <Link href={item.href}>
                    <item.icon className="size-4" />
                    <span>{item.title}</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            ))}
          </SidebarMenu>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel>Operacao</SidebarGroupLabel>
          <SidebarMenu>
            {supportItems.map((item) => (
              <SidebarMenuItem key={item.title}>
                <SidebarMenuButton asChild>
                  <Link href={item.href}>
                    <item.icon className="size-4" />
                    <span>{item.title}</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            ))}
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <div className="rounded-2xl border border-sidebar-border bg-sidebar-accent p-4">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-sm font-medium">Backend vetorial</p>
              <p className="text-xs text-sidebar-foreground/70">Qdrant conectado</p>
            </div>
            <Badge variant="secondary">Online</Badge>
          </div>
        </div>
      </SidebarFooter>
    </Sidebar>
  )
}
