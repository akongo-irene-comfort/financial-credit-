"use client"

import { useState, useCallback } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Upload, FileText, CheckCircle2, AlertCircle } from "lucide-react"
import { useDropzone } from "react-dropzone"

interface DataUploadSectionProps {
  onDataUploaded: (data: any) => void
}

export default function DataUploadSection({ onDataUploaded }: DataUploadSectionProps) {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState<"idle" | "success" | "error">("idle")
  const [preview, setPreview] = useState<any[]>([])

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const uploadedFile = acceptedFiles[0]
      setFile(uploadedFile)
      setUploadStatus("idle")
      
      // Parse CSV file for preview
      const reader = new FileReader()
      reader.onload = (e) => {
        const text = e.target?.result as string
        const lines = text.split("\n").filter(line => line.trim())
        const headers = lines[0].split(",").map(h => h.trim())
        const allRows = lines.slice(1).map(line => {
          const values = line.split(",")
          return headers.reduce((obj, header, index) => {
            obj[header] = values[index]?.trim() || ""
            return obj
          }, {} as any)
        }).filter(row => Object.values(row).some(v => v !== ""))
        
        setPreview(allRows.slice(0, 5))
      }
      reader.readAsText(uploadedFile)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/csv": [".csv"],
      "application/vnd.ms-excel": [".xls"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"]
    },
    multiple: false
  })

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    setUploadStatus("idle")

    // Parse full dataset
    const reader = new FileReader()
    reader.onload = (e) => {
      const text = e.target?.result as string
      const lines = text.split("\n").filter(line => line.trim())
      const headers = lines[0].split(",").map(h => h.trim())
      const allRows = lines.slice(1).map(line => {
        const values = line.split(",")
        return headers.reduce((obj, header, index) => {
          const value = values[index]?.trim() || ""
          obj[header] = value
          return obj
        }, {} as any)
      }).filter(row => Object.values(row).some(v => v !== ""))

      setTimeout(() => {
        setUploadStatus("success")
        setUploading(false)
        onDataUploaded({
          filename: file.name,
          size: file.size,
          rowCount: allRows.length,
          columnCount: headers.length,
          headers,
          rows: allRows,
          preview: allRows.slice(0, 5)
        })
      }, 1500)
    }
    reader.readAsText(file)
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5 text-success" />
            Upload Dataset
          </CardTitle>
          <CardDescription>
            Upload your loan application dataset (CSV, XLS, or XLSX format)
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div
            {...getRootProps()}
            className={`
              border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
              ${isDragActive ? "border-success bg-success/5" : "border-muted-foreground/25 hover:border-success/50"}
            `}
          >
            <input {...getInputProps()} />
            <div className="flex flex-col items-center gap-2">
              <Upload className="h-10 w-10 text-muted-foreground" />
              {isDragActive ? (
                <p className="text-sm text-muted-foreground">Drop the file here...</p>
              ) : (
                <>
                  <p className="text-sm font-medium">Drag & drop your dataset here</p>
                  <p className="text-xs text-muted-foreground">or click to browse files</p>
                </>
              )}
            </div>
          </div>

          {file && (
            <div className="flex items-center justify-between rounded-lg border p-4 bg-card">
              <div className="flex items-center gap-3">
                <FileText className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm font-medium">{file.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {(file.size / 1024).toFixed(2)} KB
                  </p>
                </div>
              </div>
              {uploadStatus === "success" && (
                <CheckCircle2 className="h-5 w-5 text-success" />
              )}
              {uploadStatus === "error" && (
                <AlertCircle className="h-5 w-5 text-destructive" />
              )}
            </div>
          )}

          <Button
            onClick={handleUpload}
            disabled={!file || uploading || uploadStatus === "success"}
            className="w-full bg-success hover:bg-success/90 text-success-foreground"
          >
            {uploading ? "Uploading..." : uploadStatus === "success" ? "✓ Uploaded Successfully" : "Upload and Process"}
          </Button>
        </CardContent>
      </Card>

      {preview.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Data Preview</CardTitle>
            <CardDescription>First 5 rows of your dataset</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/50">
                    {Object.keys(preview[0]).map((header, i) => (
                      <th key={i} className="px-4 py-2 text-left font-medium text-sm">
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {preview.map((row, i) => (
                    <tr key={i} className="border-b hover:bg-muted/30 transition-colors">
                      {Object.values(row).map((value: any, j) => (
                        <td key={j} className="px-4 py-2 text-sm">
                          {value}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}