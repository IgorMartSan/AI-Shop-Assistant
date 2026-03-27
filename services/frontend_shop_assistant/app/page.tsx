import { AppSidebar } from "@/components/app-sidebar"
import { QdrantBrowser } from "@/components/qdrant-browser"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8010"

export default function Page() {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <div className="flex items-center justify-between border-b px-4 py-4 md:px-8">
          <div className="flex items-center gap-3">
            <SidebarTrigger />
            <div>
              <p className="text-sm text-muted-foreground">Workspace</p>
              <h1 className="text-xl font-semibold">Painel da API vetorial</h1>
            </div>
          </div>
          <Badge variant="outline">NEXT_PUBLIC_API_URL</Badge>
        </div>

        <div className="flex flex-1 flex-col gap-6 p-4 md:p-8">
          <section
            id="overview"
            className="grid gap-6 rounded-[2rem] border bg-gradient-to-br from-primary/8 via-background to-chart-1/10 p-6 md:grid-cols-[1.3fr_0.7fr]"
          >
            <div className="space-y-4">
              <Badge>Frontend conectado por env</Badge>
              <div className="space-y-3">
                <h2 className="max-w-2xl text-3xl font-semibold tracking-tight">
                  Navegue pelas collections e veja os pontos cadastrados com um clique.
                </h2>
                <p className="max-w-2xl text-sm text-muted-foreground">
                  O frontend consulta a API do Qdrant pela URL configurada em
                  <strong> NEXT_PUBLIC_API_URL</strong> e atualiza a listagem no painel
                  principal.
                </p>
              </div>
            </div>

            <Card className="border-primary/15 bg-background/80 backdrop-blur">
              <CardHeader>
                <CardTitle>Conexao ativa</CardTitle>
                <CardDescription>
                  Endpoint usado para buscar collections e pontos.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="rounded-2xl bg-muted p-4 font-mono text-sm break-all">
                  {apiUrl}
                </div>
                <p className="text-sm text-muted-foreground">
                  Definida no compose como <strong>NEXT_PUBLIC_API_URL</strong>.
                </p>
              </CardContent>
            </Card>
          </section>

          <QdrantBrowser apiUrl={apiUrl} />
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
