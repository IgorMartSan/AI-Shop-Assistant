"use client"

import { useEffect, useState } from "react"
import {
  RiAddLine,
  RiDeleteBinLine,
  RiDatabase2Line,
  RiEditLine,
  RiArrowLeftSLine,
  RiArrowRightSLine,
  RiLoader4Line,
  RiMapPin2Line,
  RiRefreshLine,
  RiWifiLine,
} from "@remixicon/react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Textarea } from "@/components/ui/textarea"
type Collection = {
  name: string
}

type CollectionsResponse = {
  result: Collection[]
}

type PointRecord = {
  id: string | number
  payload?: Record<string, unknown> | null
  vector?: number[]
}

type PointsResponse = {
  result: PointRecord[]
  page: number
  limit: number
  total: number
  total_pages: number
  has_previous: boolean
  has_next: boolean
  previous_page?: number | null
  next_page?: number | null
}

type QdrantBrowserProps = {
  apiUrl: string
}

type HealthResponse = {
  message?: string
}

type MutationResponse = {
  operation_id?: number
  status?: string
}

type PayloadField = {
  key: string
  value: string
}

const PAGE_SIZE = 10

export function QdrantBrowser({ apiUrl }: QdrantBrowserProps) {
  const [mounted, setMounted] = useState(false)
  const [collections, setCollections] = useState<Collection[]>([])
  const [selectedCollection, setSelectedCollection] = useState<string | null>(null)
  const [points, setPoints] = useState<PointRecord[]>([])
  const [currentPage, setCurrentPage] = useState(1)
  const [totalItems, setTotalItems] = useState(0)
  const [totalPages, setTotalPages] = useState(1)
  const [hasPrevious, setHasPrevious] = useState(false)
  const [hasNext, setHasNext] = useState(false)
  const [loadingCollections, setLoadingCollections] = useState(true)
  const [loadingPoints, setLoadingPoints] = useState(false)
  const [collectionsError, setCollectionsError] = useState<string | null>(null)
  const [itemsError, setItemsError] = useState<string | null>(null)
  const [testingConnection, setTestingConnection] = useState(false)
  const [connectionMessage, setConnectionMessage] = useState<string | null>(null)
  const [connectionOk, setConnectionOk] = useState<boolean | null>(null)
  const [searchTerm, setSearchTerm] = useState("")
  const [reloadKey, setReloadKey] = useState(0)
  const [createOpen, setCreateOpen] = useState(false)
  const [createName, setCreateName] = useState("")
  const [createCategory, setCreateCategory] = useState("")
  const [createDescription, setCreateDescription] = useState("")
  const [createExtraFields, setCreateExtraFields] = useState<PayloadField[]>([])
  const [editOpen, setEditOpen] = useState(false)
  const [editingPoint, setEditingPoint] = useState<PointRecord | null>(null)
  const [payloadText, setPayloadText] = useState("{}")
  const [vectorText, setVectorText] = useState("")
  const [savingPoint, setSavingPoint] = useState(false)
  const [deletingPointId, setDeletingPointId] = useState<string | number | null>(null)
  const [actionMessage, setActionMessage] = useState<string | null>(null)

  useEffect(() => {
    setMounted(true)
  }, [])

  async function testConnection() {
    setTestingConnection(true)
    setConnectionMessage(null)
    setConnectionOk(null)

    try {
      const response = await fetch(`${apiUrl}/`, {
        cache: "no-store",
      })

      if (!response.ok) {
        throw new Error(`API respondeu com status ${response.status}.`)
      }

      const data = (await response.json()) as HealthResponse

      setConnectionOk(true)
      setConnectionMessage(data.message ?? "API respondeu com sucesso.")
    } catch (err) {
      setConnectionOk(false)
      setConnectionMessage(
        err instanceof Error ? err.message : "Nao foi possivel conectar na API."
      )
    } finally {
      setTestingConnection(false)
    }
  }

  useEffect(() => {
    let cancelled = false

    async function loadCollections() {
      setLoadingCollections(true)
      setCollectionsError(null)

      try {
        const response = await fetch(`${apiUrl}/qdrant/collections`, {
          cache: "no-store",
        })

        if (!response.ok) {
          throw new Error("Nao foi possivel carregar as collections.")
        }

        const data = (await response.json()) as CollectionsResponse

        if (cancelled) {
          return
        }

        setCollections(data.result ?? [])

        if (data.result?.length) {
          setSelectedCollection((current) => current ?? data.result[0].name)
        } else {
          setSelectedCollection(null)
          setPoints([])
          setCurrentPage(1)
          setTotalItems(0)
          setTotalPages(1)
          setHasPrevious(false)
          setHasNext(false)
        }
      } catch (err) {
        if (!cancelled) {
          setCollectionsError(
            err instanceof Error ? err.message : "Erro ao carregar collections."
          )
        }
      } finally {
        if (!cancelled) {
          setLoadingCollections(false)
        }
      }
    }

    loadCollections()

    return () => {
      cancelled = true
    }
  }, [apiUrl])

  useEffect(() => {
    setCurrentPage(1)
    setTotalItems(0)
    setTotalPages(1)
    setHasPrevious(false)
    setHasNext(false)
  }, [searchTerm, selectedCollection])

  useEffect(() => {
    if (!selectedCollection) {
      return
    }

    const collectionName = selectedCollection
    const pageNumber = currentPage
    let cancelled = false

    async function loadPoints() {
      setLoadingPoints(true)
      setItemsError(null)

      try {
        const params = new URLSearchParams({
          page: String(pageNumber),
          limit: String(PAGE_SIZE),
          with_payload: "true",
          with_vector: "false",
        })
        if (searchTerm.trim()) {
          params.set("query", searchTerm.trim())
        }

        const response = await fetch(
          `${apiUrl}/qdrant/points/${encodeURIComponent(collectionName)}?${params.toString()}`,
          { cache: "no-store" }
        )

        if (!response.ok) {
          throw new Error("Nao foi possivel carregar os pontos da collection.")
        }

        const data = (await response.json()) as PointsResponse

        if (cancelled) {
          return
        }

        setPoints(data.result ?? [])
        setTotalItems(data.total ?? 0)
        setTotalPages(data.total_pages ?? 1)
        setHasPrevious(data.has_previous ?? false)
        setHasNext(data.has_next ?? false)
      } catch (err) {
        if (!cancelled) {
          setItemsError(err instanceof Error ? err.message : "Erro ao carregar os pontos.")
          setPoints([])
          setTotalItems(0)
          setTotalPages(1)
          setHasPrevious(false)
          setHasNext(false)
        }
      } finally {
        if (!cancelled) {
          setLoadingPoints(false)
        }
      }
    }

    loadPoints()

    return () => {
      cancelled = true
    }
  }, [apiUrl, currentPage, reloadKey, searchTerm, selectedCollection])

  function selectCollection(collectionName: string) {
    setSelectedCollection(collectionName)
    setPoints([])
    setItemsError(null)
    setActionMessage(null)
    setSearchTerm("")
  }

  function goToNextPage() {
    if (!hasNext) {
      return
    }

    setCurrentPage((current) => current + 1)
  }

  function goToPreviousPage() {
    if (!hasPrevious) {
      return
    }
    setCurrentPage((current) => Math.max(1, current - 1))
  }

  function formatPayload(payload: Record<string, unknown> | null | undefined) {
    if (!payload || Object.keys(payload).length === 0) {
      return "-"
    }

    return JSON.stringify(payload)
  }

  function openEditDialog(point: PointRecord) {
    setEditingPoint(point)
    setPayloadText(JSON.stringify(point.payload ?? {}, null, 2))
    setVectorText(point.vector?.length ? JSON.stringify(point.vector, null, 2) : "")
    setItemsError(null)
    setActionMessage(null)
    setEditOpen(true)
  }

  function openCreateDialog() {
    setCreateName("")
    setCreateCategory("")
    setCreateDescription("")
    setCreateExtraFields([])
    setItemsError(null)
    setActionMessage(null)
    setCreateOpen(true)
  }

  function addCreatePayloadField() {
    setCreateExtraFields((current) => [...current, { key: "", value: "" }])
  }

  function updateCreatePayloadField(index: number, field: "key" | "value", value: string) {
    setCreateExtraFields((current) =>
      current.map((item, itemIndex) =>
        itemIndex === index ? { ...item, [field]: value } : item
      )
    )
  }

  function removeCreatePayloadField(index: number) {
    setCreateExtraFields((current) => current.filter((_, itemIndex) => itemIndex !== index))
  }

  async function handleCreatePoint() {
    if (!selectedCollection) {
      return
    }

    setSavingPoint(true)
    setItemsError(null)
    setActionMessage(null)

    try {
      const payload: Record<string, unknown> = {}

      if (!createDescription.trim()) {
        throw new Error("Informe a description do item.")
      }

      if (createName.trim()) {
        payload.name = createName.trim()
      }

      if (createCategory.trim()) {
        payload.category = createCategory.trim()
      }

      if (createDescription.trim()) {
        payload.description = createDescription.trim()
      }

      for (const field of createExtraFields) {
        const key = field.key.trim()
        if (!key) {
          throw new Error("Preencha a chave dos campos extras ou remova a linha vazia.")
        }
        payload[key] = field.value.trim()
      }

      const body = {
        collection_name: selectedCollection,
        points: [
          {
            embedding_input: createDescription.trim(),
            payload,
          },
        ],
      }

      const response = await fetch(`${apiUrl}/qdrant/points`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => null)
        throw new Error(errorData?.detail ?? "Nao foi possivel criar o item.")
      }

      const data = (await response.json()) as MutationResponse
      setActionMessage(data.status ?? "Item criado com sucesso.")
      setCreateOpen(false)
      setCurrentPage(1)
      setReloadKey((current) => current + 1)
    } catch (err) {
      setItemsError(err instanceof Error ? err.message : "Erro ao criar o item.")
    } finally {
      setSavingPoint(false)
    }
  }

  async function handleUpdatePoint() {
    if (!selectedCollection || !editingPoint) {
      return
    }

    setSavingPoint(true)
    setItemsError(null)
    setActionMessage(null)

    try {
      const payload = payloadText.trim() ? JSON.parse(payloadText) : {}
      const body: Record<string, unknown> = { payload }

      if (vectorText.trim()) {
        body.vector = JSON.parse(vectorText)
      }

      const response = await fetch(
        `${apiUrl}/qdrant/points/${encodeURIComponent(selectedCollection)}/${encodeURIComponent(String(editingPoint.id))}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        }
      )

      if (!response.ok) {
        const errorData = await response.json().catch(() => null)
        throw new Error(errorData?.detail ?? "Nao foi possivel atualizar o item.")
      }

      const data = (await response.json()) as MutationResponse
      setActionMessage(data.status ?? "Item atualizado com sucesso.")
      setEditOpen(false)
      setEditingPoint(null)
      setReloadKey((current) => current + 1)
    } catch (err) {
      setItemsError(err instanceof Error ? err.message : "Erro ao atualizar o item.")
    } finally {
      setSavingPoint(false)
    }
  }

  async function handleDeletePoint(pointId: string | number) {
    if (!selectedCollection) {
      return
    }

    setDeletingPointId(pointId)
    setItemsError(null)
    setActionMessage(null)

    try {
      const response = await fetch(
        `${apiUrl}/qdrant/points/${encodeURIComponent(selectedCollection)}/${encodeURIComponent(String(pointId))}`,
        { method: "DELETE" }
      )

      if (!response.ok) {
        const errorData = await response.json().catch(() => null)
        throw new Error(errorData?.detail ?? "Nao foi possivel deletar o item.")
      }

      const data = (await response.json()) as MutationResponse
      setActionMessage(data.status ?? "Item deletado com sucesso.")

      if (points.length === 1 && currentPage > 1) {
        setCurrentPage((current) => Math.max(1, current - 1))
      } else {
        setReloadKey((current) => current + 1)
      }
    } catch (err) {
      setItemsError(err instanceof Error ? err.message : "Erro ao deletar o item.")
    } finally {
      setDeletingPointId(null)
    }
  }

  if (!mounted) {
    return (
      <div className="grid gap-6">
        <Card id="collections">
          <CardHeader>
            <CardTitle>Collections</CardTitle>
            <CardDescription>Carregando interface...</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 rounded-2xl border p-4 text-sm text-muted-foreground">
              <RiLoader4Line className="size-4 animate-spin" />
              Inicializando pagina...
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="grid gap-6">
      <Card id="collections">
        <CardHeader className="space-y-4">
          <div className="flex items-center justify-between gap-3">
            <div>
              <CardTitle>Collections</CardTitle>
              <CardDescription>Selecione uma collection no dropdown para carregar os itens.</CardDescription>
            </div>
            <Button
              variant="outline"
              size="icon"
              onClick={() => window.location.reload()}
              aria-label="Atualizar collections"
            >
              <RiRefreshLine />
            </Button>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="secondary">{collections.length} encontradas</Badge>
            <Badge variant="outline" className="max-w-full truncate">
              {apiUrl}
            </Badge>
            {connectionMessage ? (
              <Badge variant={connectionOk ? "secondary" : "outline"}>{connectionMessage}</Badge>
            ) : null}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {collectionsError ? (
            <div className="rounded-2xl border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive">
              {collectionsError}
            </div>
          ) : null}

          {loadingCollections ? (
            <div className="flex items-center gap-2 rounded-2xl border p-4 text-sm text-muted-foreground">
              <RiLoader4Line className="size-4 animate-spin" />
              Carregando collections...
            </div>
          ) : null}

          {!loadingCollections && !collectionsError && collections.length === 0 ? (
            <div className="rounded-2xl border border-dashed p-4 text-sm text-muted-foreground">
              Nenhuma collection encontrada.
            </div>
          ) : null}

          <div className="grid gap-4 lg:grid-cols-[minmax(0,280px)_minmax(0,1fr)_auto]">
            <div className="space-y-2">
              <p className="text-sm font-medium">Collection</p>
              <Select
                value={selectedCollection ?? undefined}
                onValueChange={selectCollection}
                disabled={loadingCollections || collections.length === 0}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Selecione uma collection" />
                </SelectTrigger>
                <SelectContent>
                  {collections.map((collection) => (
                    <SelectItem key={collection.name} value={collection.name}>
                      {collection.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <p className="text-sm font-medium">Pesquisar itens</p>
              <Input
                value={searchTerm}
                onChange={(event) => setSearchTerm(event.target.value)}
                placeholder="Pesquisar por id, payload, texto, numero..."
                disabled={!selectedCollection}
              />
            </div>

            <div className="flex items-end">
              <Button
                variant="outline"
                onClick={testConnection}
                disabled={testingConnection}
                className="w-full lg:w-auto"
              >
                {testingConnection ? (
                  <RiLoader4Line className="animate-spin" />
                ) : (
                  <RiWifiLine />
                )}
                testar api
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <CardTitle>
                {selectedCollection ? selectedCollection : "Selecione uma collection"}
              </CardTitle>
              <CardDescription>
                {selectedCollection
                  ? "Itens cadastrados em tabela, com filtro por payload e demais dados."
                  : "Escolha uma collection no dropdown acima para listar os itens."}
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="secondary">{points.length} itens na pagina</Badge>
              <Badge variant="outline">{totalItems} itens encontrados</Badge>
              <Badge variant="outline">
                Pagina {currentPage} de {totalPages}
              </Badge>
              {loadingPoints ? <Badge variant="outline">Carregando</Badge> : null}
            </div>
          </div>
          {selectedCollection ? (
            <div className="flex flex-wrap items-center justify-between gap-3">
              <p className="text-sm text-muted-foreground">
                Mostrando ate {PAGE_SIZE} registros por pagina. Total de itens: {totalItems}.
              </p>
              <div className="flex items-center gap-2">
                <Dialog open={createOpen} onOpenChange={setCreateOpen}>
                  <DialogTrigger asChild>
                    <Button size="sm" onClick={openCreateDialog}>
                      <RiAddLine />
                      criar item
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-2xl">
                    <DialogHeader>
                      <DialogTitle>Criar item em {selectedCollection}</DialogTitle>
                      <DialogDescription>
                        Informe os dados do ponto. O backend gera o embedding a partir do texto enviado.
                      </DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4">
                      <div className="space-y-2">
                        <p className="text-sm font-medium">Payload</p>
                        <div className="grid gap-3 md:grid-cols-2">
                          <div className="space-y-2">
                            <p className="text-xs text-muted-foreground">Name</p>
                            <Input
                              value={createName}
                              onChange={(event) => setCreateName(event.target.value)}
                              placeholder="Notebook Dell"
                            />
                          </div>
                          <div className="space-y-2">
                            <p className="text-xs text-muted-foreground">Category</p>
                            <Input
                              value={createCategory}
                              onChange={(event) => setCreateCategory(event.target.value)}
                              placeholder="informatica"
                            />
                          </div>
                        </div>
                        <div className="space-y-2">
                          <p className="text-xs text-muted-foreground">
                            Description
                          </p>
                          <Textarea
                            value={createDescription}
                            onChange={(event) => setCreateDescription(event.target.value)}
                            className="min-h-24"
                            placeholder="Notebook com RTX 4060 e SSD de 1TB"
                          />
                          <p className="text-xs text-muted-foreground">
                            Esse mesmo texto sera usado para gerar o embedding.
                          </p>
                        </div>
                        <div className="space-y-3 rounded-2xl border p-3">
                          <div className="flex items-center justify-between gap-2">
                            <p className="text-sm font-medium">Campos extras</p>
                            <Button type="button" variant="outline" size="sm" onClick={addCreatePayloadField}>
                              <RiAddLine />
                              add campo
                            </Button>
                          </div>
                          {createExtraFields.length === 0 ? (
                            <p className="text-xs text-muted-foreground">
                              Nenhum campo extra adicionado.
                            </p>
                          ) : null}
                          {createExtraFields.map((field, index) => (
                            <div key={index} className="grid gap-2 md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto]">
                              <Input
                                value={field.key}
                                onChange={(event) =>
                                  updateCreatePayloadField(index, "key", event.target.value)
                                }
                                placeholder="key"
                              />
                              <Input
                                value={field.value}
                                onChange={(event) =>
                                  updateCreatePayloadField(index, "value", event.target.value)
                                }
                                placeholder="value"
                              />
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                onClick={() => removeCreatePayloadField(index)}
                              >
                                remover
                              </Button>
                            </div>
                          ))}
                        </div>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        O ID e gerado automaticamente como UUID no momento da criacao.
                      </p>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setCreateOpen(false)}>
                        cancelar
                      </Button>
                      <Button onClick={handleCreatePoint} disabled={savingPoint}>
                        {savingPoint ? "criando..." : "criar"}
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={goToPreviousPage}
                  disabled={loadingPoints || !hasPrevious}
                >
                  <RiArrowLeftSLine />
                  anterior
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={goToNextPage}
                  disabled={loadingPoints || !hasNext}
                >
                  proxima
                  <RiArrowRightSLine />
                </Button>
              </div>
            </div>
          ) : null}
          <Separator />
        </CardHeader>
        <CardContent className="space-y-4">
          {itemsError ? (
            <div className="rounded-2xl border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive">
              {itemsError}
            </div>
          ) : null}

          {actionMessage ? (
            <div className="rounded-2xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-700">
              {actionMessage}
            </div>
          ) : null}

          {!selectedCollection && !itemsError ? (
            <div className="rounded-[1.5rem] border border-dashed p-8 text-center text-sm text-muted-foreground">
              Nenhuma collection selecionada.
            </div>
          ) : null}

          {selectedCollection && loadingPoints ? (
            <div className="flex items-center gap-2 rounded-2xl border p-4 text-sm text-muted-foreground">
              <RiLoader4Line className="size-4 animate-spin" />
              Carregando pontos da collection...
            </div>
          ) : null}

          {selectedCollection && !loadingPoints && points.length === 0 && !itemsError ? (
            <div className="rounded-[1.5rem] border border-dashed p-8 text-center text-sm text-muted-foreground">
              Esta collection nao possui pontos cadastrados.
            </div>
          ) : null}

          {selectedCollection && !loadingPoints && points.length === 0 && totalItems > 0 ? (
            <div className="rounded-[1.5rem] border border-dashed p-8 text-center text-sm text-muted-foreground">
              Nenhum item encontrado para a busca atual.
            </div>
          ) : null}

          {points.length > 0 ? (
            <div className="overflow-hidden rounded-[1.5rem] border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-32">ID</TableHead>
                    <TableHead className="w-40">Payload</TableHead>
                    <TableHead>Conteudo indexado para busca</TableHead>
                    <TableHead className="w-44 text-right">Acoes</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {points.map((point) => {
                    return (
                      <TableRow key={String(point.id)}>
                        <TableCell className="font-mono">{String(point.id)}</TableCell>
                        <TableCell className="max-w-80">
                          <div className="flex items-center gap-2 text-sm text-muted-foreground">
                            <RiMapPin2Line className="size-4 shrink-0" />
                            <span className="truncate">{formatPayload(point.payload)}</span>
                          </div>
                        </TableCell>
                        <TableCell className="max-w-0">
                          <div className="truncate text-sm text-muted-foreground">
                            {[String(point.id), JSON.stringify(point.payload ?? {}), JSON.stringify(point.vector ?? [])].join(" ")}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center justify-end gap-2">
                            <Dialog
                              open={editOpen && editingPoint?.id === point.id}
                              onOpenChange={(open) => {
                                setEditOpen(open)
                                if (!open) {
                                  setEditingPoint(null)
                                }
                              }}
                            >
                              <DialogTrigger asChild>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => openEditDialog(point)}
                                >
                                  <RiEditLine />
                                  atualizar
                                </Button>
                              </DialogTrigger>
                              <DialogContent className="sm:max-w-2xl">
                                <DialogHeader>
                                  <DialogTitle>Atualizar item {String(point.id)}</DialogTitle>
                                  <DialogDescription>
                                    Edite o payload em JSON. O vector e opcional.
                                  </DialogDescription>
                                </DialogHeader>
                                <div className="grid gap-4">
                                  <div className="space-y-2">
                                    <p className="text-sm font-medium">Payload JSON</p>
                                    <Textarea
                                      value={payloadText}
                                      onChange={(event) => setPayloadText(event.target.value)}
                                      className="min-h-44 font-mono text-xs"
                                    />
                                  </div>
                                  <div className="space-y-2">
                                    <p className="text-sm font-medium">Vector JSON (opcional)</p>
                                    <Textarea
                                      value={vectorText}
                                      onChange={(event) => setVectorText(event.target.value)}
                                      className="min-h-28 font-mono text-xs"
                                      placeholder="[0.12, -0.45, 0.91]"
                                    />
                                  </div>
                                </div>
                                <DialogFooter>
                                  <Button
                                    variant="outline"
                                    onClick={() => {
                                      setEditOpen(false)
                                      setEditingPoint(null)
                                    }}
                                  >
                                    cancelar
                                  </Button>
                                  <Button onClick={handleUpdatePoint} disabled={savingPoint}>
                                    {savingPoint ? "salvando..." : "salvar"}
                                  </Button>
                                </DialogFooter>
                              </DialogContent>
                            </Dialog>

                            <AlertDialog>
                              <AlertDialogTrigger asChild>
                                <Button
                                  variant="destructive"
                                  size="sm"
                                  disabled={deletingPointId === point.id}
                                >
                                  <RiDeleteBinLine />
                                  deletar
                                </Button>
                              </AlertDialogTrigger>
                              <AlertDialogContent>
                                <AlertDialogHeader>
                                  <AlertDialogTitle>Deletar item {String(point.id)}?</AlertDialogTitle>
                                  <AlertDialogDescription>
                                    Essa acao remove o ponto da collection selecionada.
                                  </AlertDialogDescription>
                                </AlertDialogHeader>
                                <AlertDialogFooter>
                                  <AlertDialogCancel>cancelar</AlertDialogCancel>
                                  <AlertDialogAction
                                    variant="destructive"
                                    onClick={() => handleDeletePoint(point.id)}
                                  >
                                    confirmar
                                  </AlertDialogAction>
                                </AlertDialogFooter>
                              </AlertDialogContent>
                            </AlertDialog>
                          </div>
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            </div>
          ) : null}
        </CardContent>
      </Card>
    </div>
  )
}
